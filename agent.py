import os
from typing import List, Dict, Any
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage, HumanMessage
from langchain.tools import BaseTool
from chatbortai.tools import FileSearchTool, FileReaderTool, ASTParserTool, DirectoryListerTool
from chatbortai.vector_store import CodeVectorStore
from chatbortai.config import Config
from chatbortai.demo_llm import DemoLLM
from chatbortai.demo_agent import DemoAgent

class CodePalAgent:
    """Main agent class for CodePal chatbot"""
    
    def __init__(self, vector_store: CodeVectorStore = None):
        self.vector_store = vector_store
        self.llm = None
        self.agent = None
        self.agent_executor = None
        self.tools = []
        
        # Initialize LLM
        self._initialize_llm()
        
        # Initialize tools
        self._initialize_tools()
        
        # Initialize agent
        self._initialize_agent()
    
    def _initialize_llm(self):
        """Initialize the language model"""
        if Config.LLM_PROVIDER.lower() == "demo":
            # Initialize Demo LLM (no external API required)
            self.llm = DemoLLM()
        elif Config.LLM_PROVIDER.lower() == "ollama":
            # Initialize Ollama
            self.llm = ChatOllama(
                model=Config.OLLAMA_MODEL,
                base_url=Config.OLLAMA_BASE_URL,
                temperature=0.1
            )
        else:
            # Initialize OpenAI (default)
            if not Config.OPENAI_API_KEY:
                raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in your environment.")
            
            self.llm = ChatOpenAI(
                model=Config.LLM_MODEL,
                temperature=0.1,
                api_key=Config.OPENAI_API_KEY
            )
    
    def _initialize_tools(self):
        """Initialize all tools"""
        # File search tool
        if self.vector_store:
            self.tools.append(FileSearchTool(self.vector_store, self.vector_store.embedding_model))
        
        # File reader tool
        self.tools.append(FileReaderTool())
        
        # AST parser tool
        self.tools.append(ASTParserTool())
        
        # Directory lister tool
        self.tools.append(DirectoryListerTool())
    
    def _initialize_agent(self):
        """Initialize the agent with tools and prompt"""
        
        # System prompt
        system_prompt = """You are CodePal, an intelligent AI assistant that helps developers understand and navigate code repositories. 

Your capabilities:
1. You can search for files and code snippets using semantic search
2. You can read and analyze file contents
3. You can parse Python files to extract functions, classes, and imports
4. You can list directory contents to understand repository structure

When answering questions:
1. THINK: Break down the user's question to understand what they need
2. ACT: Choose the appropriate tool(s) to gather information
3. OBSERVE: Analyze the results from your tools
4. SYNTHESIZE: Provide a comprehensive, well-structured answer

Always be helpful, accurate, and provide context about where you found the information. If you cannot find the requested information, be honest about it and suggest alternative approaches.

Current working directory: {working_directory}"""

        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )
    
    def ask(self, question: str, chat_history: List = None) -> str:
        """Ask a question and get a response"""
        if chat_history is None:
            chat_history = []
        
        try:
            # Check if we're using demo mode
            if Config.LLM_PROVIDER.lower() == "demo":
                # Use the demo agent directly
                demo_agent = DemoAgent(self.vector_store)
                return demo_agent.ask(question, chat_history)
            
            # Get current working directory
            working_directory = os.getcwd()
            
            # Prepare input
            agent_input = {
                "input": question,
                "chat_history": chat_history,
                "working_directory": working_directory
            }
            
            # Execute agent
            result = self.agent_executor.invoke(agent_input)
            
            return result.get("output", "I couldn't process your request.")
            
        except Exception as e:
            return f"I encountered an error while processing your question: {str(e)}"
    
    def update_vector_store(self, vector_store: CodeVectorStore):
        """Update the vector store and reinitialize tools"""
        self.vector_store = vector_store
        self.tools = []
        self._initialize_tools()
        self._initialize_agent()
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names"""
        return [tool.name for tool in self.tools]

class CodePalManager:
    """Manager class for CodePal operations"""
    
    def __init__(self):
        self.vector_store = None
        self.agent = None
        self.processor = None
    
    def initialize_repository(self, repo_path: str, force_reprocess: bool = False) -> str:
        """Initialize a repository for analysis"""
        try:
            # Check if vector store already exists
            vector_store_path = os.path.join(Config.VECTOR_STORE_PATH, "code_vectors")
            
            if not force_reprocess and os.path.exists(vector_store_path):
                # Try to load existing vector store
                self.vector_store = CodeVectorStore()
                if self.vector_store.load(vector_store_path):
                    self.agent = CodePalAgent(self.vector_store)
                    return f"Loaded existing vector store for repository: {repo_path}"
            
            # Process repository
            from chatbortai.vector_store import CodeProcessor
            self.processor = CodeProcessor()
            
            # Process files
            documents = self.processor.process_repository(repo_path)
            
            if not documents:
                return f"No supported files found in repository: {repo_path}"
            
            # Create vector store
            self.vector_store = CodeVectorStore()
            self.vector_store.add_documents(documents)
            self.vector_store.create_embeddings()
            
            # Save vector store
            self.vector_store.save(vector_store_path)
            
            # Initialize agent
            self.agent = CodePalAgent(self.vector_store)
            
            return f"Successfully processed {len(documents)} documents from repository: {repo_path}"
            
        except Exception as e:
            return f"Error initializing repository: {str(e)}"
    
    def ask_question(self, question: str, chat_history: List = None) -> str:
        """Ask a question to the agent"""
        if not self.agent:
            return "Please initialize a repository first before asking questions."
        
        return self.agent.ask(question, chat_history)
    
    def get_repository_info(self) -> Dict[str, Any]:
        """Get information about the current repository"""
        if not self.vector_store:
            return {"status": "No repository loaded"}
        
        return {
            "status": "Repository loaded",
            "total_documents": len(self.vector_store.documents),
            "available_tools": self.agent.get_available_tools() if self.agent else []
        } 