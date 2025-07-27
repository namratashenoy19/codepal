import os
import ast
from pathlib import Path
from typing import List, Dict, Any, Optional
from langchain.tools import BaseTool
from langchain.schema import Document
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from chatbortai.config import Config

class FileSearchTool(BaseTool):
    """Tool for semantic search across the codebase"""
    
    name: str = "file_search_tool"
    description: str = "Search for files or code snippets related to a query using semantic search"
    
    def __init__(self, vector_store, embedding_model):
        super().__init__()
        # Store as private attributes to avoid Pydantic field validation
        self._vector_store = vector_store
        self._embedding_model = embedding_model
    
    def _run(self, query: str) -> str:
        """Perform semantic search and return relevant results"""
        try:
            # Encode the query
            query_embedding = self._embedding_model.encode([query])
            
            # Search in vector store
            if self._vector_store is not None and hasattr(self._vector_store, 'faiss_index'):
                D, I = self._vector_store.faiss_index.search(query_embedding.astype('float32'), k=5)
                
                results = []
                for idx in I[0]:
                    if idx < len(self._vector_store.documents):
                        doc = self._vector_store.documents[idx]
                        results.append(f"File: {doc.metadata.get('file_path', 'Unknown')}\n"
                                     f"Content: {doc.page_content[:200]}...\n")
                
                if results:
                    return "\n".join(results)
                else:
                    return "No relevant files found for the query."
            else:
                return "Vector store not properly initialized."
                
        except Exception as e:
            return f"Error during file search: {str(e)}"

class FileReaderTool(BaseTool):
    """Tool for reading file contents"""
    
    name: str = "file_reader_tool"
    description: str = "Read and return the contents of a specific file"
    
    def _run(self, file_path: str) -> str:
        """Read file contents and return them"""
        try:
            if not os.path.exists(file_path):
                return f"File not found: {file_path}"
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > Config.MAX_FILE_SIZE:
                return f"File too large to read ({file_size} bytes). Maximum allowed: {Config.MAX_FILE_SIZE} bytes"
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return f"File: {file_path}\n\nContent:\n{content}"
            
        except Exception as e:
            return f"Error reading file {file_path}: {str(e)}"

class ASTParserTool(BaseTool):
    """Tool for analyzing Python code structure using AST"""
    
    name: str = "ast_parser_tool"
    description: str = "Analyze Python file structure and extract functions, classes, and imports"
    
    def _run(self, file_path: str) -> str:
        """Parse Python file and extract structural information"""
        try:
            if not file_path.endswith('.py'):
                return "This tool only works with Python (.py) files"
            
            if not os.path.exists(file_path):
                return f"File not found: {file_path}"
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Extract information
            functions = []
            classes = []
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    else:
                        module = node.module or ""
                        for alias in node.names:
                            imports.append(f"{module}.{alias.name}")
            
            result = f"File: {file_path}\n\n"
            
            if imports:
                result += f"Imports ({len(imports)}):\n"
                for imp in imports:
                    result += f"  - {imp}\n"
                result += "\n"
            
            if classes:
                result += f"Classes ({len(classes)}):\n"
                for cls in classes:
                    result += f"  - {cls}\n"
                result += "\n"
            
            if functions:
                result += f"Functions ({len(functions)}):\n"
                for func in functions:
                    result += f"  - {func}\n"
            
            if not any([imports, classes, functions]):
                result += "No functions, classes, or imports found in this file."
            
            return result
            
        except SyntaxError as e:
            return f"Syntax error in {file_path}: {str(e)}"
        except Exception as e:
            return f"Error parsing {file_path}: {str(e)}"

class DirectoryListerTool(BaseTool):
    """Tool for listing directory contents"""
    
    name: str = "directory_lister_tool"
    description: str = "List all files and subdirectories within a given directory"
    
    def _run(self, directory_path: str) -> str:
        """List directory contents"""
        try:
            if not os.path.exists(directory_path):
                return f"Directory not found: {directory_path}"
            
            if not os.path.isdir(directory_path):
                return f"Path is not a directory: {directory_path}"
            
            result = f"Directory: {directory_path}\n\n"
            
            # Get all items in directory
            items = os.listdir(directory_path)
            
            if not items:
                result += "Directory is empty."
                return result
            
            # Separate files and directories
            files = []
            directories = []
            
            for item in items:
                item_path = os.path.join(directory_path, item)
                if os.path.isdir(item_path):
                    directories.append(item)
                else:
                    files.append(item)
            
            # Sort alphabetically
            directories.sort()
            files.sort()
            
            if directories:
                result += f"Subdirectories ({len(directories)}):\n"
                for dir_name in directories:
                    result += f"  📁 {dir_name}/\n"
                result += "\n"
            
            if files:
                result += f"Files ({len(files)}):\n"
                for file_name in files:
                    # Add file extension indicator
                    ext = os.path.splitext(file_name)[1]
                    if ext in Config.SUPPORTED_EXTENSIONS:
                        result += f"  📄 {file_name}\n"
                    else:
                        result += f"  📄 {file_name} (unsupported type)\n"
            
            return result
            
        except Exception as e:
            return f"Error listing directory {directory_path}: {str(e)}" 