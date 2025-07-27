#!/usr/bin/env python3
"""
Test script for CodePal functionality.
This script tests the core components without requiring the web interface.
"""

import os
import sys
from chatbortai.agent import CodePalManager

def test_codepal():
    """Test CodePal functionality with the sample repository"""
    
    print("🤖 Testing CodePal - AI Code Assistant")
    print("=" * 50)
    
    # Initialize CodePal manager
    print("1. Initializing CodePal manager...")
    manager = CodePalManager()
    
    # Test with sample repository
    sample_repo_path = "sample_repo"
    if not os.path.exists(sample_repo_path):
        print(f"❌ Sample repository not found at: {sample_repo_path}")
        return False
    
    print(f"2. Processing sample repository: {sample_repo_path}")
    result = manager.initialize_repository(sample_repo_path)
    print(f"   Result: {result}")
    
    # Get repository info
    print("3. Getting repository information...")
    repo_info = manager.get_repository_info()
    print(f"   Status: {repo_info['status']}")
    if repo_info['status'] == "Repository loaded":
        print(f"   Total documents: {repo_info['total_documents']}")
        print(f"   Available tools: {', '.join(repo_info['available_tools'])}")
    
    # Test questions
    test_questions = [
        "What is the purpose of the database_connector.py file?",
        "Explain the calculate_user_permissions function to me. Where is it defined?",
        "Which files in the repository seem to be related to payment processing?",
        "List all the functions inside the api/routes.py file.",
        "What classes are defined in the models directory?"
    ]
    
    print("\n4. Testing questions...")
    for i, question in enumerate(test_questions, 1):
        print(f"\n   Question {i}: {question}")
        print("   " + "-" * 40)
        
        try:
            response = manager.ask_question(question)
            print(f"   Response: {response[:200]}...")
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n✅ CodePal test completed!")
    return True

def main():
    """Main function"""
    try:
        success = test_codepal()
        if success:
            print("\n🎉 All tests passed! CodePal is working correctly.")
            print("\nTo run the web interface:")
            print("1. Set your OpenAI API key in environment variables")
            print("2. Run: streamlit run app.py")
        else:
            print("\n❌ Some tests failed. Please check the errors above.")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 