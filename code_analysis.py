import ast
import os
from typing import List, Dict, Optional

def extract_functions(file_path: str) -> List[Dict]:
    """Extract function names and their docstrings from a Python file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read(), filename=file_path)
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            doc = ast.get_docstring(node)
            functions.append({
                'name': node.name,
                'lineno': node.lineno,
                'docstring': doc
            })
    return functions

def extract_classes(file_path: str) -> List[Dict]:
    """Extract class names and their docstrings from a Python file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read(), filename=file_path)
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            doc = ast.get_docstring(node)
            classes.append({
                'name': node.name,
                'lineno': node.lineno,
                'docstring': doc
            })
    return classes

def summarize_file(file_path: str) -> str:
    """Summarize the purpose of a Python file using its top-level docstring or comments."""
    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()
    try:
        tree = ast.parse(source, filename=file_path)
        doc = ast.get_docstring(tree)
        if doc:
            return doc
    except Exception:
        pass
    # Fallback: use first comment block
    for line in source.splitlines():
        if line.strip().startswith('#'):
            return line.strip('#').strip()
    return "No summary available."

def list_python_files(directory: str) -> List[str]:
    """Recursively list all Python files in a directory."""
    py_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))
    return py_files

def extract_classes_in_directory(directory: str) -> Dict[str, List[Dict]]:
    """List all classes in all Python files in a directory."""
    result = {}
    for file_path in list_python_files(directory):
        classes = extract_classes(file_path)
        if classes:
            result[file_path] = classes
    return result 