#!/usr/bin/env python3
"""
Demo script for CodePal - AI Code Assistant
This script demonstrates all the features and capabilities of CodePal.
"""

import os
import sys
import time
from chatbortai.agent import CodePalManager

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"🤖 {title}")
    print("=" * 60)

def print_section(title):
    """Print a formatted section header"""
    print(f"\n📋 {title}")
    print("-" * 40)

def demo_initialization():
    """Demonstrate repository initialization"""
    print_section("Repository Initialization")
    
    manager = CodePalManager()
    
    # Initialize with sample repository
    sample_repo_path = "sample_repo"
    if not os.path.exists(sample_repo_path):
        print("❌ Sample repository not found. Please ensure sample_repo directory exists.")
        return None
    
    print(f"📁 Processing repository: {sample_repo_path}")
    result = manager.initialize_repository(sample_repo_path)
    print(f"✅ {result}")
    
    # Show repository info
    repo_info = manager.get_repository_info()
    print(f"📊 Repository Status: {repo_info['status']}")
    if repo_info['status'] == "Repository loaded":
        print(f"📄 Total Documents: {repo_info['total_documents']}")
        print(f"🛠️ Available Tools: {', '.join(repo_info['available_tools'])}")
    
    return manager

def demo_semantic_search(manager):
    """Demonstrate semantic search capabilities"""
    print_section("Semantic Search Demo")
    
    search_queries = [
        "database connection",
        "user authentication",
        "payment processing",
        "API endpoints",
        "password validation"
    ]
    
    for query in search_queries:
        print(f"\n🔍 Searching for: '{query}'")
        response = manager.ask_question(f"Find files related to {query}")
        print(f"📝 Response: {response[:150]}...")

def demo_file_analysis(manager):
    """Demonstrate file analysis capabilities"""
    print_section("File Analysis Demo")
    
    analysis_requests = [
        "What is the purpose of the database_connector.py file?",
        "Show me the structure of the api/routes.py file",
        "What functions are available in the models/user.py file?",
        "Explain the User class in the user model"
    ]
    
    for request in analysis_requests:
        print(f"\n📖 Analyzing: '{request}'")
        response = manager.ask_question(request)
        print(f"📝 Response: {response[:200]}...")

def demo_ast_parsing(manager):
    """Demonstrate AST parsing capabilities"""
    print_section("AST Parsing Demo")
    
    ast_requests = [
        "List all functions in database_connector.py",
        "Show me all classes in models/user.py",
        "What imports are used in api/routes.py?",
        "Parse the structure of database_connector.py"
    ]
    
    for request in ast_requests:
        print(f"\n🔧 AST Parsing: '{request}'")
        response = manager.ask_question(request)
        print(f"📝 Response: {response[:200]}...")

def demo_directory_navigation(manager):
    """Demonstrate directory navigation"""
    print_section("Directory Navigation Demo")
    
    navigation_requests = [
        "List the contents of the sample_repo directory",
        "What files are in the api directory?",
        "Show me the structure of the models directory",
        "What's the overall structure of this repository?"
    ]
    
    for request in navigation_requests:
        print(f"\n📁 Navigation: '{request}'")
        response = manager.ask_question(request)
        print(f"📝 Response: {response[:200]}...")

def demo_complex_queries(manager):
    """Demonstrate complex multi-step queries"""
    print_section("Complex Queries Demo")
    
    complex_queries = [
        "How does the authentication system work in this codebase?",
        "Explain the user permission system and how it's implemented",
        "What are the different user roles and what can each role do?",
        "How is the database connection handled and what types are supported?",
        "Show me the payment processing flow from API to database"
    ]
    
    for query in complex_queries:
        print(f"\n🧠 Complex Query: '{query}'")
        response = manager.ask_question(query)
        print(f"📝 Response: {response[:300]}...")

def demo_error_handling(manager):
    """Demonstrate error handling"""
    print_section("Error Handling Demo")
    
    error_queries = [
        "What does the non_existent_function do?",
        "Show me the contents of imaginary_file.py",
        "List all functions in a file that doesn't exist",
        "What's in the /path/to/nowhere directory?"
    ]
    
    for query in error_queries:
        print(f"\n⚠️ Error Test: '{query}'")
        response = manager.ask_question(query)
        print(f"📝 Response: {response[:200]}...")

def demo_tool_selection(manager):
    """Demonstrate intelligent tool selection"""
    print_section("Tool Selection Demo")
    
    tool_demo_queries = [
        "Find files that contain payment-related code",
        "Read the contents of database_connector.py",
        "Parse the structure of models/user.py",
        "List all files in the api directory"
    ]
    
    for query in tool_demo_queries:
        print(f"\n🛠️ Tool Selection: '{query}'")
        response = manager.ask_question(query)
        print(f"📝 Response: {response[:200]}...")

def main():
    """Main demo function"""
    print_header("CodePal - AI Code Assistant Demo")
    
    print("🎯 This demo showcases all the features of CodePal:")
    print("   • Semantic search across codebase")
    print("   • File content analysis")
    print("   • AST parsing for Python files")
    print("   • Directory navigation")
    print("   • Complex multi-step reasoning")
    print("   • Error handling and graceful failures")
    print("   • Intelligent tool selection")
    
    # Initialize
    manager = demo_initialization()
    if not manager:
        print("❌ Failed to initialize CodePal. Exiting.")
        sys.exit(1)
    
    # Run demos
    demo_semantic_search(manager)
    demo_file_analysis(manager)
    demo_ast_parsing(manager)
    demo_directory_navigation(manager)
    demo_complex_queries(manager)
    demo_error_handling(manager)
    demo_tool_selection(manager)
    
    print_header("Demo Completed Successfully!")
    print("🎉 All CodePal features have been demonstrated!")
    print("\n💡 Key Takeaways:")
    print("   • CodePal can understand and analyze code repositories")
    print("   • It uses multiple tools intelligently to answer questions")
    print("   • It provides comprehensive and contextual answers")
    print("   • It handles errors gracefully")
    print("   • It can perform complex multi-step reasoning")
    
    print("\n🚀 Next Steps:")
    print("   • Try the web interface: streamlit run app.py")
    print("   • Ask your own questions about the codebase")
    print("   • Upload your own repository for analysis")
    print("   • Explore the different tools and capabilities")

if __name__ == "__main__":
    main() 