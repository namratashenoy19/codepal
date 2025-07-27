import os
from typing import List, Dict, Any
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from chatbortai.tools import FileSearchTool, FileReaderTool, ASTParserTool, DirectoryListerTool

class DemoAgent:
    """Demo agent that actually uses tools to analyze uploaded code"""
    
    def __init__(self, vector_store=None):
        self.vector_store = vector_store
        self.tools = []
        self.analysis_cache = {}  # Cache previous analyses
        self.question_count = {}  # Track how many times each type of question is asked
        self._initialize_tools()
    
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
    
    def ask(self, question: str, chat_history: List = None) -> str:
        """Process question and use tools to provide real analysis"""
        if chat_history is None:
            chat_history = []
        
        try:
            question_lower = question.lower()
            
            # First, try to understand the specific question and provide a direct answer
            return self._answer_specific_question(question, question_lower, chat_history)
                
        except Exception as e:
            return f"I encountered an error while analyzing your code: {str(e)}"
    
    def _answer_specific_question(self, question: str, question_lower: str, chat_history: List) -> str:
        """Answer the specific question asked by the user"""
        try:
            # Look for specific file names in the question
            if any(ext in question_lower for ext in ['.py', '.js', '.ts', '.java', '.cpp']):
                return self._answer_about_specific_file(question, question_lower)
            
            # Look for specific function/class names
            if 'what is' in question_lower or 'explain' in question_lower:
                return self._explain_code_element(question, question_lower)
            
            # Look for "how many" questions
            if 'how many' in question_lower:
                return self._count_code_elements(question, question_lower)
            
            # Look for "where is" or "find" questions
            if any(phrase in question_lower for phrase in ['where is', 'where are', 'find', 'locate']):
                return self._find_code_elements(question, question_lower)
            
            # Look for "list" or "show me" questions
            if any(phrase in question_lower for phrase in ['list', 'show me', 'display', 'get all']):
                return self._list_code_elements(question, question_lower)
            
            # Default to intelligent analysis based on keywords
            return self._intelligent_analysis(question, question_lower)
            
        except Exception as e:
            return f"I encountered an error while processing your question: {str(e)}"
    
    def _answer_about_specific_file(self, question: str, question_lower: str) -> str:
        """Answer questions about specific files"""
        # Extract filename from question
        words = question.split()
        filename = None
        for word in words:
            if any(ext in word for ext in ['.py', '.js', '.ts', '.java', '.cpp']):
                filename = word.strip('.,!?')
                break
        
        if filename:
            try:
                # Check if file exists and read it
                file_tool = FileReaderTool()
                file_content = file_tool._run(filename)
                
                if "File not found" in file_content:
                    return f"I couldn't find the file '{filename}' in your uploaded code. Here are the files I can see:\n\n" + self._list_available_files()
                
                # Analyze the specific file
                result = f"# 📄 Analysis of {filename}\n\n"
                
                if filename.endswith('.py'):
                    ast_tool = ASTParserTool()
                    ast_analysis = ast_tool._run(filename)
                    result += ast_analysis + "\n\n"
                
                # Add relevant content based on question
                if 'function' in question_lower:
                    lines = file_content.split('\n')
                    func_lines = [line for line in lines if 'def ' in line]
                    if func_lines:
                        result += "## Function Definitions:\n"
                        for func_line in func_lines:
                            result += f"```python\n{func_line.strip()}\n```\n"
                
                return result
                
            except Exception as e:
                return f"Error analyzing {filename}: {str(e)}"
        
        return "I couldn't identify which specific file you're asking about. Could you specify the filename?"
    
    def _explain_code_element(self, question: str, question_lower: str) -> str:
        """Explain specific code elements"""
        result = f"# 🔍 Explanation for: '{question}'\n\n"
        
        # Try to find what they're asking about
        if 'function' in question_lower:
            # Look for function name in question
            words = question.split()
            for word in words:
                if word not in ['what', 'is', 'the', 'function', 'explain', 'how', 'does']:
                    # This might be a function name
                    result += f"Looking for function '{word}' in your code...\n\n"
                    return self._search_for_element(word, 'function')
        
        elif 'class' in question_lower:
            words = question.split()
            for word in words:
                if word not in ['what', 'is', 'the', 'class', 'explain', 'how', 'does']:
                    result += f"Looking for class '{word}' in your code...\n\n"
                    return self._search_for_element(word, 'class')
        
        return result + "I need more specific information. Could you ask about a specific function, class, or file name?"
    
    def _count_code_elements(self, question: str, question_lower: str) -> str:
        """Count specific elements in the code"""
        result = f"# 📊 Counting Elements: '{question}'\n\n"
        
        try:
            if 'function' in question_lower:
                return self._count_functions()
            elif 'class' in question_lower:
                return self._count_classes()
            elif 'file' in question_lower:
                return self._count_files()
            elif 'import' in question_lower:
                return self._count_imports()
        except Exception as e:
            result += f"Error counting: {str(e)}\n"
        
        return result + "I can count functions, classes, files, or imports. What would you like me to count?"
    
    def _find_code_elements(self, question: str, question_lower: str) -> str:
        """Find specific code elements"""
        result = f"# 🔍 Search Results for: '{question}'\n\n"
        
        # Extract what they're looking for
        words = question.split()
        search_terms = []
        for word in words:
            if word not in ['where', 'is', 'are', 'find', 'locate', 'the', 'a', 'an']:
                search_terms.append(word)
        
        if search_terms:
            search_query = ' '.join(search_terms)
            return self._search_code(search_query)
        
        return result + "What specifically are you looking for? Please provide more details."
    
    def _list_code_elements(self, question: str, question_lower: str) -> str:
        """List specific code elements"""
        if 'function' in question_lower:
            return self._analyze_functions(1)
        elif 'class' in question_lower:
            return self._analyze_classes(1)
        elif 'import' in question_lower:
            return self._analyze_imports(1)
        elif 'file' in question_lower:
            return self._analyze_structure(1)
        else:
            return self._general_analysis(1)
    
    def _intelligent_analysis(self, question: str, question_lower: str) -> str:
        """Provide intelligent analysis based on question content"""
        # Determine question type and track repetitions
        question_type = self._get_question_type(question_lower)
        self.question_count[question_type] = self.question_count.get(question_type, 0) + 1
        
        # Analyze the question and decide which tools to use
        if any(word in question_lower for word in ["function", "def", "method"]):
            return self._analyze_functions(self.question_count[question_type])
        
        elif any(word in question_lower for word in ["class", "object", "inheritance"]):
            return self._analyze_classes(self.question_count[question_type])
        
        elif any(word in question_lower for word in ["import", "dependency", "module"]):
            return self._analyze_imports(self.question_count[question_type])
        
        elif any(word in question_lower for word in ["file", "structure", "directory"]):
            return self._analyze_structure(self.question_count[question_type])
        
        elif any(word in question_lower for word in ["search", "find"]):
            return self._search_code(question)
        
        else:
            return self._general_analysis(self.question_count[question_type])
    
    def _search_for_element(self, element_name: str, element_type: str) -> str:
        """Search for a specific element in the code"""
        result = f"# 🔍 Searching for {element_type}: '{element_name}'\n\n"
        
        try:
            # Search through Python files
            dir_tool = DirectoryListerTool()
            files_info = dir_tool._run(".")
            
            python_files = []
            if "📄" in files_info:
                lines = files_info.split('\n')
                for line in lines:
                    if ".py" in line and "📄" in line:
                        filename = line.split("📄")[-1].strip()
                        if filename and not filename.startswith("("):
                            python_files.append(filename)
            
            found_in_files = []
            file_tool = FileReaderTool()
            
            for py_file in python_files:
                try:
                    file_content = file_tool._run(py_file)
                    if element_name in file_content:
                        found_in_files.append(py_file)
                        
                        # Extract relevant lines
                        lines = file_content.split('\n')
                        relevant_lines = []
                        for i, line in enumerate(lines):
                            if element_name in line:
                                # Get context (line before and after)
                                start = max(0, i-1)
                                end = min(len(lines), i+2)
                                context = lines[start:end]
                                relevant_lines.extend(context)
                        
                        if relevant_lines:
                            result += f"## Found in {py_file}:\n```python\n"
                            result += '\n'.join(relevant_lines[:10])  # Limit output
                            result += "\n```\n"
                except:
                    continue
            
            if found_in_files:
                result += f"✅ Found '{element_name}' in {len(found_in_files)} files: {', '.join(found_in_files)}\n"
            else:
                result += f"❌ Could not find '{element_name}' in your uploaded Python files.\n"
                result += "Available files: " + ', '.join(python_files) + "\n"
                
        except Exception as e:
            result += f"Error during search: {str(e)}\n"
        
        return result
    
    def _count_functions(self) -> str:
        """Count total functions across all files"""
        result = "# 📊 Function Count Analysis\n\n"
        
        try:
            dir_tool = DirectoryListerTool()
            files_info = dir_tool._run(".")
            
            python_files = []
            if "📄" in files_info:
                lines = files_info.split('\n')
                for line in lines:
                    if ".py" in line and "📄" in line:
                        filename = line.split("📄")[-1].strip()
                        if filename and not filename.startswith("("):
                            python_files.append(filename)
            
            total_functions = 0
            file_function_counts = {}
            
            ast_tool = ASTParserTool()
            for py_file in python_files:
                try:
                    analysis = ast_tool._run(py_file)
                    if "Functions (" in analysis:
                        func_count_str = analysis.split("Functions (")[1].split(")")[0]
                        try:
                            func_count = int(func_count_str)
                            file_function_counts[py_file] = func_count
                            total_functions += func_count
                        except:
                            pass
                except:
                    continue
            
            result += f"**Total Functions Found: {total_functions}**\n\n"
            result += "## Functions per file:\n"
            for filename, count in file_function_counts.items():
                result += f"- {filename}: {count} functions\n"
                
        except Exception as e:
            result += f"Error counting functions: {str(e)}\n"
        
        return result
    
    def _count_classes(self) -> str:
        """Count total classes across all files"""
        result = "# 📊 Class Count Analysis\n\n"
        
        try:
            dir_tool = DirectoryListerTool()
            files_info = dir_tool._run(".")
            
            python_files = []
            if "📄" in files_info:
                lines = files_info.split('\n')
                for line in lines:
                    if ".py" in line and "📄" in line:
                        filename = line.split("📄")[-1].strip()
                        if filename and not filename.startswith("("):
                            python_files.append(filename)
            
            total_classes = 0
            file_class_counts = {}
            
            ast_tool = ASTParserTool()
            for py_file in python_files:
                try:
                    analysis = ast_tool._run(py_file)
                    if "Classes (" in analysis:
                        class_count_str = analysis.split("Classes (")[1].split(")")[0]
                        try:
                            class_count = int(class_count_str)
                            file_class_counts[py_file] = class_count
                            total_classes += class_count
                        except:
                            pass
                except:
                    continue
            
            result += f"**Total Classes Found: {total_classes}**\n\n"
            result += "## Classes per file:\n"
            for filename, count in file_class_counts.items():
                result += f"- {filename}: {count} classes\n"
                
        except Exception as e:
            result += f"Error counting classes: {str(e)}\n"
        
        return result
    
    def _count_files(self) -> str:
        """Count files by type"""
        result = "# 📊 File Count Analysis\n\n"
        
        try:
            dir_tool = DirectoryListerTool()
            files_info = dir_tool._run(".")
            
            file_types = {}
            total_files = 0
            
            lines = files_info.split('\n')
            for line in lines:
                if "📄" in line:
                    total_files += 1
                    if "." in line:
                        # Extract file extension
                        parts = line.split(".")
                        if len(parts) > 1:
                            ext = parts[-1].split()[0]  # Get extension before any other text
                            file_types[ext] = file_types.get(ext, 0) + 1
            
            result += f"**Total Files: {total_files}**\n\n"
            result += "## Files by type:\n"
            for ext, count in sorted(file_types.items()):
                result += f"- .{ext}: {count} files\n"
                
        except Exception as e:
            result += f"Error counting files: {str(e)}\n"
        
        return result
    
    def _count_imports(self) -> str:
        """Count total imports across all files"""
        result = "# 📊 Import Count Analysis\n\n"
        
        try:
            dir_tool = DirectoryListerTool()
            files_info = dir_tool._run(".")
            
            python_files = []
            if "📄" in files_info:
                lines = files_info.split('\n')
                for line in lines:
                    if ".py" in line and "📄" in line:
                        filename = line.split("📄")[-1].strip()
                        if filename and not filename.startswith("("):
                            python_files.append(filename)
            
            total_imports = 0
            all_imports = set()
            
            ast_tool = ASTParserTool()
            for py_file in python_files:
                try:
                    analysis = ast_tool._run(py_file)
                    if "Imports (" in analysis:
                        import_count_str = analysis.split("Imports (")[1].split(")")[0]
                        try:
                            import_count = int(import_count_str)
                            total_imports += import_count
                            
                            # Extract import names
                            lines = analysis.split('\n')
                            for line in lines:
                                if line.strip().startswith('- '):
                                    import_name = line.strip()[2:]
                                    all_imports.add(import_name)
                        except:
                            pass
                except:
                    continue
            
            result += f"**Total Import Statements: {total_imports}**\n"
            result += f"**Unique Imports: {len(all_imports)}**\n\n"
            
            if all_imports:
                result += "## Most common imports:\n"
                for imp in sorted(list(all_imports))[:15]:  # Show top 15
                    result += f"- {imp}\n"
                
        except Exception as e:
            result += f"Error counting imports: {str(e)}\n"
        
        return result
    
    def _list_available_files(self) -> str:
        """List all available files"""
        try:
            dir_tool = DirectoryListerTool()
            return dir_tool._run(".")
        except:
            return "Could not list files."
    
    def _get_question_type(self, question_lower: str) -> str:
        """Determine the type of question being asked"""
        if any(word in question_lower for word in ["function", "def", "method"]):
            return "functions"
        elif any(word in question_lower for word in ["class", "object", "inheritance"]):
            return "classes"
        elif any(word in question_lower for word in ["import", "dependency", "module"]):
            return "imports"
        elif any(word in question_lower for word in ["file", "structure", "directory"]):
            return "structure"
        elif any(word in question_lower for word in ["search", "find"]):
            return "search"
        else:
            return "general"
    
    def _analyze_functions(self, repeat_count: int = 1) -> str:
        """Analyze functions in uploaded code with varying detail based on repeat count"""
        if repeat_count == 1:
            result = "# 🔍 Function Analysis\n\n"
        elif repeat_count == 2:
            result = "# 🔍 Detailed Function Analysis (Round 2)\n\n"
        else:
            result = f"# 🔍 Deep Function Analysis (Request #{repeat_count})\n\n"
        
        # Try to find Python files and analyze them
        try:
            # Use directory lister to find files
            dir_tool = DirectoryListerTool()
            files_info = dir_tool._run(".")
            
            # Look for Python files
            python_files = []
            if "📄" in files_info:
                lines = files_info.split('\n')
                for line in lines:
                    if ".py" in line and "📄" in line:
                        # Extract filename
                        filename = line.split("📄")[-1].strip()
                        if filename and not filename.startswith("("):
                            python_files.append(filename)
            
            if python_files:
                result += f"Found {len(python_files)} Python files. Analyzing functions...\n\n"
                
                # Analyze each Python file with varying detail
                ast_tool = ASTParserTool()
                file_limit = min(3 + repeat_count, len(python_files))  # Show more files on repeat
                
                for py_file in python_files[:file_limit]:
                    try:
                        analysis = ast_tool._run(py_file)
                        result += f"## {py_file}\n{analysis}\n\n"
                        
                        # Add more detail on repeat questions
                        if repeat_count > 1:
                            try:
                                file_tool = FileReaderTool()
                                file_content = file_tool._run(py_file)
                                # Extract just function definitions for detailed view
                                lines = file_content.split('\n')
                                func_lines = [line for line in lines if 'def ' in line]
                                if func_lines:
                                    result += f"### Function Signatures in {py_file}:\n"
                                    for func_line in func_lines[:5]:  # Show first 5 function signatures
                                        result += f"```python\n{func_line.strip()}\n```\n"
                                    result += "\n"
                            except:
                                pass
                    except:
                        result += f"## {py_file}\nCould not analyze this file.\n\n"
            else:
                result += "No Python files found in uploaded code. Upload some .py files to see function analysis.\n"
                
        except Exception as e:
            result += f"Error during analysis: {str(e)}\n"
        
        return result

    def _analyze_classes(self, repeat_count: int = 1) -> str:
        """Analyze classes in uploaded code with varying detail"""
        if repeat_count == 1:
            result = "# 🏗️ Class Analysis\n\n"
        elif repeat_count == 2:
            result = "# 🏗️ Detailed Class Structure Analysis\n\n"
        else:
            result = f"# 🏗️ In-Depth Class Analysis (Request #{repeat_count})\n\n"
        
        try:
            # Similar to function analysis but focus on classes
            dir_tool = DirectoryListerTool()
            files_info = dir_tool._run(".")
            
            python_files = []
            if "📄" in files_info:
                lines = files_info.split('\n')
                for line in lines:
                    if ".py" in line and "📄" in line:
                        filename = line.split("📄")[-1].strip()
                        if filename and not filename.startswith("("):
                            python_files.append(filename)
            
            if python_files:
                result += f"Analyzing classes in {len(python_files)} Python files...\n\n"
                
                ast_tool = ASTParserTool()
                file_limit = min(3 + repeat_count, len(python_files))
                
                for py_file in python_files[:file_limit]:
                    try:
                        analysis = ast_tool._run(py_file)
                        if "Classes" in analysis:
                            result += f"## {py_file}\n{analysis}\n\n"
                            
                            # Add class method details on repeat
                            if repeat_count > 1:
                                try:
                                    file_tool = FileReaderTool()
                                    file_content = file_tool._run(py_file)
                                    lines = file_content.split('\n')
                                    class_lines = [line for line in lines if 'class ' in line]
                                    if class_lines:
                                        result += f"### Class Definitions in {py_file}:\n"
                                        for class_line in class_lines:
                                            result += f"```python\n{class_line.strip()}\n```\n"
                                        result += "\n"
                                except:
                                    pass
                    except:
                        continue
            else:
                result += "No Python files found. Upload .py files to see class analysis.\n"
                
        except Exception as e:
            result += f"Error during analysis: {str(e)}\n"
        
        return result
    
    def _analyze_imports(self, repeat_count: int = 1) -> str:
        """Analyze imports in uploaded code with varying perspectives"""
        if repeat_count == 1:
            result = "# 📦 Import Analysis\n\n"
        elif repeat_count == 2:
            result = "# 📦 Dependency Deep Dive\n\n"
        else:
            result = f"# 📦 Complete Import Mapping (Analysis #{repeat_count})\n\n"
        
        try:
            dir_tool = DirectoryListerTool()
            files_info = dir_tool._run(".")
            
            python_files = []
            if "📄" in files_info:
                lines = files_info.split('\n')
                for line in lines:
                    if ".py" in line and "📄" in line:
                        filename = line.split("📄")[-1].strip()
                        if filename and not filename.startswith("("):
                            python_files.append(filename)
            
            if python_files:
                result += f"Analyzing imports in {len(python_files)} Python files...\n\n"
                
                ast_tool = ASTParserTool()
                all_imports = set()
                
                for py_file in python_files[:5]:
                    try:
                        analysis = ast_tool._run(py_file)
                        if "Imports" in analysis:
                            result += f"## {py_file}\n{analysis}\n\n"
                            # Extract imports for summary
                            lines = analysis.split('\n')
                            for line in lines:
                                if line.strip().startswith('- '):
                                    import_name = line.strip()[2:]
                                    all_imports.add(import_name)
                    except:
                        continue
                
                if all_imports:
                    result += f"## Summary\nTotal unique imports found: {len(all_imports)}\n"
                    result += "Most common imports:\n"
                    for imp in sorted(list(all_imports))[:10]:
                        result += f"- {imp}\n"
            else:
                result += "No Python files found. Upload .py files to see import analysis.\n"
                
        except Exception as e:
            result += f"Error during analysis: {str(e)}\n"
        
        return result
    
    def _analyze_structure(self, repeat_count: int = 1) -> str:
        """Analyze project structure with different focus each time"""
        if repeat_count == 1:
            result = "# 📁 Project Structure Analysis\n\n"
        elif repeat_count == 2:
            result = "# 📁 Detailed File Organization Review\n\n"
        else:
            result = f"# 📁 Complete Project Architecture (View #{repeat_count})\n\n"
        
        try:
            dir_tool = DirectoryListerTool()
            structure = dir_tool._run(".")
            result += structure
            
            # Count different file types
            lines = structure.split('\n')
            file_types = {}
            total_files = 0
            
            for line in lines:
                if "📄" in line:
                    total_files += 1
                    if "." in line:
                        ext = line.split(".")[-1].split()[0]
                        file_types[ext] = file_types.get(ext, 0) + 1
            
            if file_types:
                result += f"\n## File Type Summary\nTotal files: {total_files}\n\n"
                for ext, count in sorted(file_types.items()):
                    result += f"- .{ext}: {count} files\n"
                    
        except Exception as e:
            result += f"Error during analysis: {str(e)}\n"
        
        return result
    
    def _search_code(self, query: str) -> str:
        """Search through uploaded code"""
        result = f"# 🔍 Search Results for: '{query}'\n\n"
        
        try:
            if self.vector_store and hasattr(self.vector_store, 'faiss_index'):
                search_tool = FileSearchTool(self.vector_store, self.vector_store.embedding_model)
                search_results = search_tool._run(query)
                result += search_results
            else:
                result += "Vector search not available. Upload and process files first.\n"
                
        except Exception as e:
            result += f"Error during search: {str(e)}\n"
        
        return result
    
    def _general_analysis(self, repeat_count: int = 1) -> str:
        """Provide general analysis with different insights each time"""
        if repeat_count == 1:
            result = "# 📊 General Code Analysis\n\n"
        elif repeat_count == 2:
            result = "# 📊 Code Quality & Architecture Overview\n\n"
        else:
            result = f"# 📊 Comprehensive Code Review (Round #{repeat_count})\n\n"
        
        try:
            # Get file structure
            dir_tool = DirectoryListerTool()
            structure = dir_tool._run(".")
            
            if "📄" in structure:
                result += "## Files Uploaded\n"
                result += structure + "\n\n"
                
                # Quick analysis of Python files
                lines = structure.split('\n')
                python_files = []
                for line in lines:
                    if ".py" in line and "📄" in line:
                        filename = line.split("📄")[-1].strip()
                        if filename and not filename.startswith("("):
                            python_files.append(filename)
                
                if python_files:
                    result += f"## Quick Python Analysis\nFound {len(python_files)} Python files:\n\n"
                    
                    ast_tool = ASTParserTool()
                    total_functions = 0
                    total_classes = 0
                    
                    for py_file in python_files[:3]:
                        try:
                            analysis = ast_tool._run(py_file)
                            # Count functions and classes
                            if "Functions (" in analysis:
                                func_count = analysis.split("Functions (")[1].split(")")[0]
                                try:
                                    total_functions += int(func_count)
                                except:
                                    pass
                            if "Classes (" in analysis:
                                class_count = analysis.split("Classes (")[1].split(")")[0]
                                try:
                                    total_classes += int(class_count)
                                except:
                                    pass
                        except:
                            continue
                    
                    result += f"- Total functions found: {total_functions}\n"
                    result += f"- Total classes found: {total_classes}\n\n"
                    
                result += "💡 **Ask me specific questions like:**\n"
                result += "- 'What functions are in my code?'\n"
                result += "- 'Show me all classes'\n"
                result += "- 'What imports do I use?'\n"
                result += "- 'Search for database code'\n"
            else:
                result += "No files detected. Please upload your code files first.\n"
                
        except Exception as e:
            result += f"Error during analysis: {str(e)}\n"
        
        return result
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names"""
        return [tool.name for tool in self.tools]