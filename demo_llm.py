from typing import List, Dict, Any, Optional
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.chat_models.base import BaseChatModel

class DemoLLM(BaseChatModel):
    """Demo Chat Model that provides basic responses without external API calls"""
    
    @property
    def _llm_type(self) -> str:
        return "demo"
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> Any:
        from langchain.schema import ChatGeneration, ChatResult
        
        # Extract the last human message
        prompt = ""
        for message in messages:
            if isinstance(message, HumanMessage):
                prompt = message.content
                break
        
        response_text = self._get_demo_response(prompt)
        
        # Create proper ChatGeneration
        message = AIMessage(content=response_text)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])
    
    def _get_demo_response(self, prompt: str) -> str:
        """Generate a demo response that encourages tool usage"""
        
        # Check if this looks like a tool call or agent reasoning
        if "Action:" in prompt or "Thought:" in prompt or "tool" in prompt.lower():
            # This is likely agent reasoning, provide a more dynamic response
            return """I'll analyze your uploaded code to provide specific information. Let me use the available tools to examine your files and give you detailed insights about your codebase.

Based on your question, I should:
1. First search through your uploaded files to find relevant code
2. Read specific files that match your query
3. Parse Python files to extract detailed information
4. Provide you with concrete examples from your actual code

Let me examine your uploaded files now..."""
        
        # For regular user questions, provide more engaging responses
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["function", "def", "method"]):
            return """I'll analyze the functions in your uploaded code files. Let me examine each file to find:

📋 **Function Analysis:**
- Function names and signatures
- Parameters and return types
- Documentation strings
- Function complexity and purpose

🔍 **What I'll look for:**
- Main entry point functions
- Helper/utility functions
- Class methods and static methods
- Async functions and generators

Let me scan through your uploaded files to provide specific details about the functions in YOUR code..."""

        elif any(word in prompt_lower for word in ["class", "object", "inheritance"]):
            return """I'll examine the classes in your uploaded code. Let me analyze:

🏗️ **Class Structure:**
- Class names and inheritance hierarchy
- Methods and properties
- Constructor parameters
- Class documentation

🔍 **Analysis includes:**
- Base classes and inheritance patterns
- Instance methods vs class methods
- Private/protected members
- Design patterns used

Scanning your uploaded files for class definitions..."""

        elif any(word in prompt_lower for word in ["import", "dependency", "module", "package"]):
            return """I'll analyze the imports and dependencies in your code. Let me examine:

📦 **Import Analysis:**
- Standard library imports
- Third-party package dependencies
- Local module imports
- Import patterns and organization

🔍 **Dependency mapping:**
- External libraries used
- Internal module relationships
- Potential circular imports
- Unused imports

Let me check the import statements in your uploaded files..."""

        elif any(word in prompt_lower for word in ["file", "structure", "directory", "organization"]):
            return """I'll examine your project structure and file organization:

📁 **Project Structure:**
- File types and extensions
- Directory organization
- Configuration files
- Documentation files

🗂️ **Code organization:**
- Main application files
- Test files
- Configuration and setup files
- Resource and data files

Analyzing the structure of your uploaded files..."""

        else:
            return """I'm ready to analyze your uploaded code! I can help you understand:

🔍 **Code Analysis:**
- Functions, classes, and their relationships
- Import dependencies and module structure
- Code patterns and architecture
- File organization and project structure

💡 **Ask me specific questions like:**
- "What functions are defined in my Python files?"
- "Show me all the classes and their methods"
- "What external libraries does my code use?"
- "Explain the structure of my project"
- "Find all the database-related code"

I'll examine your actual uploaded files and provide specific insights about YOUR code. What would you like to know?"""

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get the identifying parameters."""
        return {"type": "demo"}