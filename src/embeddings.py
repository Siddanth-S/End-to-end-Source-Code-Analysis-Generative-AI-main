import google.generativeai as genai
import os
from typing import List
import warnings
from langchain.llms.base import LLM
from google.generativeai import GenerativeModel

warnings.filterwarnings('ignore', category=DeprecationWarning)
os.environ['GRPC_VERBOSITY'] = 'ERROR'

class GoogleGeminiEmbeddings:
    """Custom embeddings using Google Gemini API"""
    
    def __init__(self, api_key: str, model: str = "models/gemini-embedding-001"):
        self.api_key = api_key
        self.model = model
        genai.configure(api_key=api_key)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            result = genai.embed_content(model=self.model, content=text)
            embeddings.append(result['embedding'])
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        result = genai.embed_content(model=self.model, content=text)
        return result['embedding']

class GeminiLLM(LLM):
    """Wrapper for Google Gemini"""
    model_name: str = "gemini-2.5-flash"
    
    def _call(self, prompt: str, stop=None) -> str:
        model = GenerativeModel(self.model_name)
        response = model.generate_content(prompt)
        return response.text
    
    @property
    def _llm_type(self) -> str:
        return "gemini"