from langchain.document_loaders import PythonLoader
from pathlib import Path

def load_python_documents(repo_path):
    """Load all Python files from a repository"""
    documents = []
    for py_file in Path(repo_path).rglob("*.py"):
        try:
            loader = PythonLoader(str(py_file))
            documents.extend(loader.load())
        except Exception as e:
            print(f"Error loading {py_file}: {e}")
    return documents