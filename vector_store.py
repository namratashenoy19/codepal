import os
import pickle
from pathlib import Path
from typing import List, Dict, Any
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from chatbortai.config import Config
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from chatbortai.code_analysis import summarize_file, extract_functions, extract_classes

class CodeVectorStore:
    """Vector store for code repository embeddings"""
    
    def __init__(self, embedding_model_name: str = None):
        self.embedding_model_name = embedding_model_name or Config.EMBEDDING_MODEL
        self.embedding_model = self._initialize_embedding_model()
        self.documents = []
        self.embeddings = None
        self.faiss_index = None
        self.docstore = DocumentStore()
    
    def _initialize_embedding_model(self):
        """Initialize embedding model with retry logic and timeout handling"""
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                # Configure requests session with longer timeout and retry strategy
                session = requests.Session()
                retry_strategy = Retry(
                    total=3,
                    backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504],
                )
                adapter = HTTPAdapter(max_retries=retry_strategy)
                session.mount("http://", adapter)
                session.mount("https://", adapter)
                
                # Try to load the model with extended timeout
                print(f"Attempting to load embedding model: {self.embedding_model_name} (attempt {attempt + 1}/{max_retries})")
                
                # Use a simpler model as fallback if the main one fails
                if attempt == 0:
                    model_name = self.embedding_model_name
                else:
                    # Fallback to a smaller, faster model
                    model_name = "paraphrase-MiniLM-L3-v2"
                
                embedding_model = SentenceTransformer(
                    model_name,
                    device='cpu',  # Force CPU to avoid GPU memory issues
                    cache_folder="./model_cache"  # Cache models locally
                )
                
                print(f"Successfully loaded embedding model: {model_name}")
                return embedding_model
                
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    print("All attempts failed. Using fallback embedding method.")
                    # Create a simple fallback embedding model
                    return self._create_fallback_embedding_model()
    
    def _create_fallback_embedding_model(self):
        """Create a simple fallback embedding model using basic text features"""
        class FallbackEmbeddingModel:
            def __init__(self):
                self.dimension = 128  # Fixed dimension for fallback
                
            def encode(self, texts, **kwargs):
                """Simple fallback encoding using basic text features"""
                import hashlib
                import numpy as np
                
                embeddings = []
                for text in texts:
                    # Create a simple hash-based embedding
                    text_hash = hashlib.md5(text.encode()).hexdigest()
                    # Convert hash to numerical values
                    embedding = np.array([ord(c) for c in text_hash[:self.dimension]], dtype=np.float32)
                    # Normalize
                    if np.linalg.norm(embedding) > 0:
                        embedding = embedding / np.linalg.norm(embedding)
                    embeddings.append(embedding)
                
                return np.array(embeddings)
        
        return FallbackEmbeddingModel()

    def add_documents(self, documents: List[Document]):
        """Add documents to the vector store"""
        self.documents.extend(documents)
    
    def create_embeddings(self):
        """Create embeddings for all documents"""
        if not self.documents:
            return
        
        # Extract text content
        texts = [doc.page_content for doc in self.documents]
        
        # Create embeddings
        embeddings = self.embedding_model.encode(texts)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.faiss_index = faiss.IndexFlatL2(dimension)
        self.faiss_index.add(embeddings.astype('float32'))
        
        # Store embeddings
        self.embeddings = embeddings
        
        # Add to document store
        for doc in self.documents:
            self.docstore.add_document(doc)
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Search for similar documents"""
        if self.faiss_index is None:
            return []
        
        # Encode query
        query_embedding = self.embedding_model.encode([query])
        
        # Search
        D, I = self.faiss_index.search(query_embedding.astype('float32'), k)
        
        # Return documents
        results = []
        for idx in I[0]:
            if idx < len(self.documents):
                results.append(self.documents[idx])
        
        return results
    
    def save(self, path: str):
        """Save vector store to disk"""
        os.makedirs(path, exist_ok=True)
        
        # Save FAISS index
        if self.faiss_index is not None:
            faiss.write_index(self.faiss_index, os.path.join(path, "faiss_index.bin"))
        
        # Save documents and metadata
        with open(os.path.join(path, "documents.pkl"), "wb") as f:
            pickle.dump(self.documents, f)
        
        # Save embedding model info
        with open(os.path.join(path, "model_info.txt"), "w") as f:
            f.write(self.embedding_model_name)
    
    def load(self, path: str):
        """Load vector store from disk"""
        if not os.path.exists(path):
            return False
        
        # Load FAISS index
        faiss_path = os.path.join(path, "faiss_index.bin")
        if os.path.exists(faiss_path):
            self.faiss_index = faiss.read_index(faiss_path)
        
        # Load documents
        docs_path = os.path.join(path, "documents.pkl")
        if os.path.exists(docs_path):
            with open(docs_path, "rb") as f:
                self.documents = pickle.load(f)
        
        # Load embedding model info
        model_info_path = os.path.join(path, "model_info.txt")
        if os.path.exists(model_info_path):
            with open(model_info_path, "r") as f:
                self.embedding_model_name = f.read().strip()
                self.embedding_model = self._initialize_embedding_model() # Re-initialize with loaded name
        
        # Recreate document store
        self.docstore = DocumentStore()
        for doc in self.documents:
            self.docstore.add_document(doc)
        
        return True

class DocumentStore:
    """Simple document store for metadata"""
    
    def __init__(self):
        self._dict = {}
        self._counter = 0
    
    def add_document(self, document: Document):
        """Add a document to the store"""
        self._dict[self._counter] = document
        self._counter += 1

class CodeProcessor:
    """Process code files and create documents for vector store"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def process_repository(self, repo_path: str) -> List[Document]:
        """Process entire repository and return documents"""
        documents = []
        repo_path = Path(repo_path)
        
        if not repo_path.exists():
            return documents
        
        # Walk through all files
        for file_path in repo_path.rglob("*"):
            if file_path.is_file() and self._should_process_file(file_path):
                file_docs = self.process_file(file_path)
                documents.extend(file_docs)
        
        return documents
    
    def process_file(self, file_path: Path) -> List[Document]:
        """Process a single file and return documents"""
        try:
            # Check file size
            if file_path.stat().st_size > Config.MAX_FILE_SIZE:
                return []
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Skip empty files
            if not content.strip():
                return []
            
            # Split content into chunks
            chunks = self.text_splitter.split_text(content)
            
            # Create documents
            documents = []
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        'file_path': str(file_path),
                        'file_name': file_path.name,
                        'file_extension': file_path.suffix,
                        'chunk_index': i,
                        'total_chunks': len(chunks)
                    }
                )
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return []
    
    def _should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed"""
        # Check extension
        if file_path.suffix not in Config.SUPPORTED_EXTENSIONS:
            return False
        
        # Skip hidden files and directories
        if any(part.startswith('.') for part in file_path.parts):
            return False
        
        # Skip common directories to ignore
        ignore_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'env'}
        if any(part in ignore_dirs for part in file_path.parts):
            return False
        
        return True 