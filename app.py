import streamlit as st
import os
import tempfile
import zipfile
from pathlib import Path
from chatbortai.agent import CodePalManager
from chatbortai.config import Config
import time

# Page configuration
st.set_page_config(
    page_title="CodePal - AI Code Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .info-box {
        background-color: #e8f5e8;
        border: 1px solid #4caf50;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3e0;
        border: 1px solid #ff9800;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #ffebee;
        border: 1px solid #f44336;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def handle_repository_initialization(repo_path, input_method="Local Path"):
    """Handle repository initialization with proper error handling"""
    try:
        with st.spinner("🔄 Processing repository... This may take a few minutes for large repositories."):
            # Add progress indicator
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Update progress
            status_text.text("Initializing AI models...")
            progress_bar.progress(25)
            time.sleep(0.5)
            
            status_text.text("Loading repository files...")
            progress_bar.progress(50)
            time.sleep(0.5)
            
            status_text.text("Creating embeddings...")
            progress_bar.progress(75)
            time.sleep(0.5)
            
            # Initialize repository
            result = st.session_state.code_pal_manager.initialize_repository(repo_path)
            
            progress_bar.progress(100)
            status_text.text("Repository loaded successfully!")
            time.sleep(1)
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            st.success("✅ Repository loaded successfully!")
            st.session_state.repository_loaded = True
            st.session_state.last_repo_path = repo_path
            
    except Exception as e:
        error_msg = str(e)
        
        # Handle specific HuggingFace timeout errors
        if "ReadTimeoutError" in error_msg and "huggingface.co" in error_msg:
            st.error("""
            ⚠️ **Connection Timeout Error**
            
            The application couldn't download the AI model due to a slow internet connection or network issues.
            
            **Solutions:**
            1. **Check your internet connection** and try again
            2. **Try again later** when network is more stable
            3. **Use a different network** (mobile hotspot, etc.)
            4. **Contact your network administrator** if behind a corporate firewall
            
            The application will retry automatically with a smaller model on the next attempt.
            """)
        else:
            st.error(f"""
            ❌ **Error initializing repository:**
            
            {error_msg}
            
            **Troubleshooting:**
            1. Make sure the repository path is correct
            2. Check if the repository contains supported file types
            3. Ensure you have read permissions for the directory
            4. Try with a smaller repository first
            """)
        
        st.session_state.repository_loaded = False

def main():
    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'code_pal_manager' not in st.session_state:
        st.session_state.code_pal_manager = CodePalManager()
    
    if 'repository_loaded' not in st.session_state:
        st.session_state.repository_loaded = False
    
    # Header
    st.markdown('<h1 class="main-header">🤖 CodePal</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your AI-powered code repository assistant</p>', unsafe_allow_html=True)
    
    # Network status warning
    if not st.session_state.repository_loaded:
        st.markdown("""
        <div class="info-box">
            <strong>💡 Tip:</strong> This application requires an internet connection to download AI models on first use. 
            If you experience timeout errors, please check your internet connection and try again.
        </div>
        """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Repository Setup")
        
        # Repository input method
        input_method = st.radio(
            "Choose input method:",
            ["Local Path", "Upload ZIP", "Upload Files"]
        )
        
        if input_method == "Local Path":
            repo_path = st.text_input(
                "Enter repository path:",
                placeholder="/path/to/your/repository"
            )
            
            if st.button("Load Repository", type="primary"):
                if repo_path and os.path.exists(repo_path):
                    handle_repository_initialization(repo_path, input_method)
                else:
                    st.error("❌ Please enter a valid repository path that exists on your system.")
        
        elif input_method == "Upload ZIP":
            uploaded_zip = st.file_uploader(
                "Upload a ZIP file containing your repository:",
                type="zip"
            )
            
            if uploaded_zip and st.button("Process ZIP", type="primary"):
                with st.spinner("Extracting and processing ZIP..."):
                    # Create temporary directory
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # Extract ZIP
                        with zipfile.ZipFile(uploaded_zip, 'r') as zip_ref:
                            zip_ref.extractall(temp_dir)
                        
                        # Find the main repository directory
                        extracted_items = os.listdir(temp_dir)
                        if len(extracted_items) == 1 and os.path.isdir(os.path.join(temp_dir, extracted_items[0])):
                            repo_path = os.path.join(temp_dir, extracted_items[0])
                        else:
                            repo_path = temp_dir
                        
                        # Process repository
                        handle_repository_initialization(repo_path, input_method)
        
        elif input_method == "Upload Files":
            uploaded_files = st.file_uploader(
                "Upload code files:",
                type=["py", "js", "ts", "java", "cpp", "c", "h", "cs", "php", "rb", "go", "rs", "swift", "kt", "scala", "r", "m", "mm", "sh", "bash", "zsh", "sql", "html", "css", "scss", "sass", "xml", "json", "yaml", "yml", "toml", "ini", "cfg", "md", "txt", "rst", "tex"],
                accept_multiple_files=True
            )
            
            if uploaded_files and st.button("Process Files", type="primary"):
                with st.spinner("Processing uploaded files..."):
                    # Create temporary directory
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # Save uploaded files
                        for uploaded_file in uploaded_files:
                            file_path = os.path.join(temp_dir, uploaded_file.name)
                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                        
                        # Process repository
                        handle_repository_initialization(temp_dir, input_method)
        
        # Repository info
        if st.session_state.repository_loaded:
            st.markdown("---")
            st.header("📊 Repository Info")
            repo_info = st.session_state.code_pal_manager.get_repository_info()
            
            if repo_info["status"] == "Repository loaded":
                st.success(f"✅ {repo_info['status']}")
                st.info(f"📄 Total documents: {repo_info['total_documents']}")
                st.info(f"🛠️ Available tools: {', '.join(repo_info['available_tools'])}")
            else:
                st.warning(f"⚠️ {repo_info['status']}")
        
        # Force reprocess option
        if st.session_state.repository_loaded:
            st.markdown("---")
            if st.button("🔄 Force Reprocess", type="secondary"):
                with st.spinner("Reprocessing repository..."):
                    # Get the last used repository path from session state
                    last_repo_path = getattr(st.session_state, 'last_repo_path', None)
                    if last_repo_path:
                        result = st.session_state.code_pal_manager.initialize_repository(
                            last_repo_path,
                            force_reprocess=True
                        )
                        st.success(result)
                    else:
                        st.error("No repository path available for reprocessing.")
    
    # Main content area
    if not st.session_state.repository_loaded:
        st.markdown("""
        <div class="info-box">
            <h3>🚀 Welcome to CodePal!</h3>
            <p>To get started:</p>
            <ol>
                <li>Use the sidebar to load your code repository</li>
                <li>Choose from local path, ZIP upload, or individual file upload</li>
                <li>Once loaded, you can ask questions about your codebase</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # Example questions
        st.markdown("### 💡 Example Questions")
        st.markdown("""
        Once you load a repository, you can ask questions like:
        - "What is the purpose of the database_connector.py file?"
        - "Explain the calculate_user_permissions function to me. Where is it defined?"
        - "Which files in the repository seem to be related to payment processing?"
        - "List all the functions inside the api/routes.py file."
        - "What classes are defined in the models directory?"
        """)
        
        # Features showcase
        st.markdown("### 🛠️ Features")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            **🔍 Semantic Search**
            - Find relevant files and code snippets
            - Understand code context and relationships
            """)
        
        with col2:
            st.markdown("""
            **📖 File Analysis**
            - Read and analyze file contents
            - Extract structural information
            """)
        
        with col3:
            st.markdown("""
            **🔧 AST Parsing**
            - Parse Python files for functions, classes, imports
            - Understand code structure
            """)
        
        with col4:
            st.markdown("""
            **📁 Directory Navigation**
            - Explore repository structure
            - List files and subdirectories
            """)
    
    else:
        # Chat interface
        st.markdown("### 💬 Ask CodePal")
        
        # Chat input
        user_question = st.chat_input("Ask a question about your codebase...")
        
        if user_question:
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            
            # Get response from agent
            with st.spinner("CodePal is thinking..."):
                response = st.session_state.code_pal_manager.ask_question(
                    user_question, 
                    st.session_state.chat_history
                )
            
            # Add assistant response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Display chat history
        if st.session_state.chat_history:
            st.markdown("### 📝 Conversation History")
            
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>👤 You:</strong><br>
                        {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <strong>🤖 CodePal:</strong><br>
                        {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Clear chat button
            if st.button("🗑️ Clear Chat History"):
                st.session_state.chat_history = []
                st.rerun()

if __name__ == "__main__":
    main() 