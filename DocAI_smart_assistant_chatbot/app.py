import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import tempfile
import logging

# LangChain se zaroori modules import karna
from langchain_community.document_loaders import PyPDFLoader, CSVLoader, TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.tools.retriever import create_retriever_tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# .env file se environment variables load karna
load_dotenv()

app = Flask(__name__)
CORS(app)

# --- GLOBAL VARIABLES ---
vector_store = None
agent_executor = None
llm = None
embeddings = None
loaded_file_names = []
all_document_chunks = [] 

# --- FILE LOADERS ---
loaders = { ".pdf": PyPDFLoader, ".txt": TextLoader, ".csv": CSVLoader }

def get_loader(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    return loaders.get(ext, lambda p: None)(file_path)

def process_and_get_chunks(files):
    all_chunks = []
    temp_files = []
    try:
        for file in files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
                file.save(tmp_file.name)
                temp_files.append(tmp_file.name)
            
            loader = get_loader(tmp_file.name)
            if loader:
                documents = loader.load()
                for doc in documents:
                    doc.metadata["source"] = file.filename
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                chunks = text_splitter.split_documents(documents)
                all_chunks.extend(chunks)
                logging.info(f"Processed {file.filename}, found {len(chunks)} chunks.")
    finally:
        for path in temp_files: os.remove(path)
    return all_chunks

def create_agent():
    global llm
    search_tool = TavilySearchResults()
    tools = [search_tool]
    if vector_store:
        retriever = vector_store.as_retriever()
        retriever_tool = create_retriever_tool(
            retriever,
            "document_search",
            "Searches the user's uploaded document(s) to answer questions."
        )
        tools.append(retriever_tool)
    prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

def initialize_components():
    global llm, embeddings, agent_executor
    logging.info("Initializing AI components...")
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0, convert_system_message_to_human=True)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    agent_executor = create_agent()
    logging.info("Search-only agent successfully created.")

initialize_components()

# --- FLASK ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_files', methods=['POST'])
def upload_files():
    global vector_store, agent_executor, loaded_file_names, all_document_chunks
    files = request.files.getlist('files')
    if not files or files[0].filename == '': return jsonify({'error': 'No files selected'}), 400
    try:
        new_file_names = [f.filename for f in files]
        loaded_file_names.extend(new_file_names)
        new_chunks = process_and_get_chunks(files)
        if not new_chunks: return jsonify({'error': 'Could not extract text from files.'}), 500
        all_document_chunks.extend(new_chunks)
        if not all_document_chunks: vector_store = None
        else: vector_store = FAISS.from_documents(all_document_chunks, embeddings)
        logging.info("Vector store successfully updated.")
        agent_executor = create_agent()
        logging.info("Agent updated with new knowledge.")
        return jsonify({
            'status': 'success', 
            'message': f'{len(files)} file(s) added to knowledge base.',
            'loaded_files': loaded_file_names
        })
    except Exception as e:
        logging.error(f"FILE UPLOAD FAILED: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/remove_file', methods=['POST'])
def remove_file():
    global vector_store, agent_executor, loaded_file_names, all_document_chunks
    data = request.get_json()
    file_to_remove = data.get('filename')
    if not file_to_remove: return jsonify({'error': 'Filename not provided'}), 400
    
    logging.info(f"--- REMOVING FILE: {file_to_remove} ---")
    
    try:
        if file_to_remove in loaded_file_names:
            loaded_file_names.remove(file_to_remove)
            logging.info(f"Removed from loaded_file_names list. Remaining: {loaded_file_names}")
        
        chunks_before = len(all_document_chunks)
        all_document_chunks = [chunk for chunk in all_document_chunks if chunk.metadata.get("source") != file_to_remove]
        chunks_after = len(all_document_chunks)
        logging.info(f"Chunks filtered. Before: {chunks_before}, After: {chunks_after}")
        
        if not all_document_chunks:
            vector_store = None
            logging.info("All files removed. Vector store is now empty.")
        else:
            vector_store = FAISS.from_documents(all_document_chunks, embeddings)
            logging.info("Vector store successfully rebuilt after file removal.")
        
        agent_executor = create_agent()
        logging.info("Agent updated after file removal.")
        
        return jsonify({
            'status': 'success',
            'message': f'"{file_to_remove}" has been removed.',
            'loaded_files': loaded_file_names
        })
    except Exception as e:
        logging.error(f"REMOVE FILE FAILED: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    # ... (existing code, no changes)
    data = request.get_json()
    query = data.get('query')
    if not query: return jsonify({'error': 'Query not provided'}), 400
    
    logging.info(f"User ka Sawal: {query}")
    try:
        result = agent_executor.invoke({"input": query})
        logging.info("Agent se jawab mil gaya!")
        return jsonify({'answer': result['output']})
    except Exception as e:
        logging.error(f"ASK FAILED: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/new_chat', methods=['POST'])
def new_chat_session():
    global vector_store, agent_executor, loaded_file_names, all_document_chunks
    logging.info("Nayi chat session shuru ho rahi hai...")
    vector_store = None
    loaded_file_names = []
    all_document_chunks = []
    agent_executor = create_agent()
    logging.info("Backend state safaltapoorvak reset ho gaya hai.")
    return jsonify({'status': 'success', 'message': 'New session started.'})

if __name__ == '__main__':
    app.run(debug=True)

