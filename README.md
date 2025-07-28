# CodePal - Intelligent Code Repository Assistant

CodePal is an AI-powered chatbot that helps developers understand and navigate large codebases. It uses an agentic AI approach with multiple tools to provide intelligent answers about code repositories.

## Features

- **Agentic AI**: Uses a reasoning loop to break down questions and choose appropriate tools
- **Semantic Search**: Vector embeddings for efficient code retrieval
- **Multiple Tools**: 
  - File search tool for semantic code search
  - File reader tool for detailed file analysis
  - AST parser tool for code structure analysis
  - Directory lister tool for repository navigation
- **Web Interface**: Clean Streamlit UI for easy interaction

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Add your OpenAI API key to .env
   ```
4. Run the application:
   ```bash
 $env:PYTHONPATH="C:\Users\namra\Downloads\chatbortai"
streamlit run chatbortai/app.py
   ```

## Usage

1. Start the application
2. Upload or specify a code repository path
3. Ask questions about the codebase in natural language
4. CodePal will use its tools to find and synthesize answers

## Example Questions

- "What is the purpose of the database_connector.py file?"
- "Explain the calculate_user_permissions function to me. Where is it defined?"
- "Which files in the repository seem to be related to payment processing?"
- "List all the functions inside the api/routes.py file."

## Architecture

- **Agent**: LangChain-based agent with custom tools
- **Vector Store**: FAISS for efficient similarity search
- **Embeddings**: Sentence transformers for code representation
- **UI**: Streamlit for web interface 
