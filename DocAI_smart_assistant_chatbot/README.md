# 🤖 SHIV-AI: The Intelligent Document & Web Assistant  

**Indian-AI — Where wisdom meets future innovations 🇮🇳**  

A futuristic AI assistant that combines the power of **Google Gemini**, **LangChain**, and **Flask** to answer queries from both uploaded documents and real-time web searches. With voice support, interactive UI, and persistent chat history, SHIV-AI is your smart companion for research, learning, and productivity.  

---

## 🔧 Features  
- Dual knowledge base: query **uploaded documents** (PDF, TXT, CSV) + **real-time web search**  
- Multi-file support with dynamic **add/remove** capability  
- Interactive futuristic UI with **light/dark mode**  
- Persistent **chat history** using localStorage  
- **Voice input (STT)** and **voice output (TTS)**  
- Feedback system with like/dislike buttons  
- Active file display to track loaded documents  

---

## 📦 Requirements  
- Python 3.9+  
- Flask  
- LangChain  
- Google Generative AI SDK  
- FAISS  
- Tavily AI  
- Tailwind CSS + JavaScript (frontend)  
- python-dotenv  

---

## 🛠 Installation  

1. Clone the repository  
```bash
git clone https://github.com/SAMUDRAGUPTA002/LLM_projects.git
cd LLM_projects/Doc_AI_smart_assistant_chatbot
````

2. Create and activate a virtual environment

```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Set up environment variables
   Create a `.env` file in the root directory and add:

```env
GOOGLE_API_KEY=your_google_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

---

## 🚀 Usage

To start the Flask server:

```bash
python app.py
```

Then open in your browser:

```
http://127.0.0.1:5000
```

---

## 📁 File Structure

```
app.py            # Main Flask application
.env              # API keys (excluded from version control)
README.md         # Project documentation
requirements.txt  # Python dependencies
/static           # Frontend assets (CSS, JS, images)
/templates        # HTML templates
```

---

## 🧠 Powered By

* Google Gemini (gemini-1.5-flash-latest)
* Google AI Embeddings (models/embedding-001)
* LangChain
* FAISS
* Tavily AI
* Flask + Tailwind CSS + JavaScript

---

## 🛡 Disclaimer

Keep your API keys **private**. Never commit `.env` files to version control.

---

## 📃 License

This project is licensed under the **MIT License**.
