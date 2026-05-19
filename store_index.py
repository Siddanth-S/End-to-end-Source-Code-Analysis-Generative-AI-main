import os
from dotenv import load_dotenv
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter, Language
from src.loader import load_python_documents
from src.embeddings import GoogleGeminiEmbeddings

load_dotenv()

api_key = os.environ.get('GOOGLE_API_KEY')

# Load documents
repo_path = "./research/test_repo/"
documents = load_python_documents(repo_path)

# Split
documents_splitter = RecursiveCharacterTextSplitter.from_language(language = Language.PYTHON,
                                                             chunk_size = 500,
                                                             chunk_overlap = 20)

texts = documents_splitter.split_documents(documents)

# Create embeddings
embeddings = GoogleGeminiEmbeddings(api_key=api_key)

# Store
vectordb = Chroma.from_documents(
    texts,
    embedding=embeddings,
    persist_directory='./db'
)

vectordb.persist()

print(f"✓ Stored {len(texts)} chunks in vector DB")