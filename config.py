import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for CodePal chatbot"""
    
    # LLM Provider Configuration
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "demo")  # "openai", "ollama", or "demo"
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # Ollama Configuration
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "codellama:7b")
    
    # Vector Store Configuration
    VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "./vector_store")
    
    # Model Configuration - Using more reliable models
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "paraphrase-MiniLM-L3-v2")  # Smaller, faster model
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")  # Used for OpenAI
    
    # Network Configuration
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))  # 30 seconds timeout
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    
    # File Processing Configuration
    SUPPORTED_EXTENSIONS = {
        '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp',
        '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt',
        '.scala', '.r', '.m', '.mm', '.sh', '.bash', '.zsh',
        '.sql', '.html', '.css', '.scss', '.sass', '.xml',
        '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg',
        '.md', '.txt', '.rst', '.tex'
    }
    
    # Maximum file size to process (in bytes)
    MAX_FILE_SIZE = 1024 * 1024  # 1MB
    
    # Chunk size for text splitting
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200