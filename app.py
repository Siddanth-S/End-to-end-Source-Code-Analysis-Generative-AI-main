import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter, Language
from src.embeddings import GoogleGeminiEmbeddings, GeminiLLM
from src.chain import create_qa_chain
from src.loader import load_python_documents
import subprocess
import shutil

load_dotenv()

app = Flask(__name__)

# Load environment variables
api_key = os.environ.get('GOOGLE_API_KEY')

# Initialize components
embeddings = GoogleGeminiEmbeddings(api_key=api_key)
llm = GeminiLLM()

# Global variable to store qa_chain
qa_chain = None

@app.route('/', methods=['GET'])
def home():
    """Serve the chat UI"""
    return render_template('index.html')

@app.route('/load-repo', methods=['POST'])
def load_repository():
    """Load a GitHub repository and create vector DB"""
    global qa_chain
    
    try:
        data = request.json
        repo_url = data.get('repo_url')
        
        if not repo_url:
            return jsonify({"error": "Repository URL is required"}), 400
        
        # Clone repository
        repo_path = './temp_repo'
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
        
        print(f"Cloning repository: {repo_url}")
        subprocess.run(['git', 'clone', repo_url, repo_path], check=True, capture_output=True)
        
        # Load documents
        print("Loading Python documents...")
        documents = load_python_documents(repo_path)
        
        if not documents:
            return jsonify({"error": "No Python files found in repository"}), 400
        
        print(f"Loaded {len(documents)} documents")
        
        # Split documents
        print("Splitting documents into chunks...")
        splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PYTHON,
            chunk_size=500,
            chunk_overlap=20
        )
        texts = splitter.split_documents(documents)
        print(f"Created {len(texts)} chunks")
        
        # Create vector DB
        print("Creating embeddings and storing in vector DB...")
        vectordb = Chroma.from_documents(
            texts,
            embedding=embeddings,
            persist_directory='./db'
        )
        vectordb.persist()
        print("Vector DB saved!")
        
        # Create QA chain
        qa_chain = create_qa_chain(llm, vectordb)
        
        # Cleanup temp repo
        shutil.rmtree(repo_path)
        
        return jsonify({
            "success": True,
            "message": f"Successfully loaded repository with {len(texts)} chunks",
            "chunks": len(texts)
        })
    
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Failed to clone repository: {str(e)}"}), 400
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error loading repository: {str(e)}"}), 500

@app.route('/get', methods=['POST'])
def get_response():
    """Handle chat messages and return answers"""
    global qa_chain
    
    if qa_chain is None:
        return "Error: Please load a repository first"
    
    user_message = request.form.get('msg')
    
    if not user_message:
        return "Please ask a question"
    
    try:
        result = qa_chain({"question": user_message})
        answer = result.get('answer', 'No answer generated')
        return answer
    except Exception as e:
        print(f"Error in Q&A chain: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error processing question: {str(e)}"

@app.route('/ask', methods=['POST'])
def ask():
    """API endpoint for JSON requests"""
    global qa_chain
    
    if qa_chain is None:
        return jsonify({"error": "Please load a repository first"}), 400
    
    data = request.json
    question = data.get('question')
    result = qa_chain({"question": question})
    return jsonify({"answer": result['answer']})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
    