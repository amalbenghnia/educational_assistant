# AI-Powered Educational Assistant 🎓

An intelligent, full-stack educational platform that enables students to interact with their course materials (PDFs) through advanced AI, Retrieval-Augmented Generation (RAG), and a modern web interface. 

This system moves beyond traditional studying by allowing students to converse with their documents, instantly generate comprehensive summaries, practice with automated quizzes, revise using flashcards, and prepare for exams—all powered by local LLMs.

---

## 🚀 Objectives

*   **Enhance Learning:** Provide students with an intelligent tutor capable of breaking down complex academic concepts from their own uploaded PDFs.
*   **Automate Study Material Generation:** Reduce the time students spend creating flashcards, quizzes, and summaries by automating the process.
*   **Privacy First:** Leverage local AI models (Llama 3 via Ollama) to ensure that academic documents and private study sessions remain strictly confidential and offline.
*   **Professional Architecture:** Build a scalable, modular, and production-ready system suitable for a final-year engineering project portfolio.

---

## ✨ Key Features

*   **📄 Multi-PDF Support:** Upload and index multiple course documents simultaneously.
*   **💬 PDF Chatbot (RAG):** Ask complex questions and get accurate answers cited with specific page references.
*   **📝 Automatic Summarization:** Generate Brief, Standard, or Detailed course explanations.
*   **🧪 Quiz Generation:** Automatically create Multiple Choice, True/False, and Short Answer quizzes with automated grading and explanations.
*   **🃏 Flashcard Generation:** Extract key concepts and definitions into interactive study flashcards.
*   **🎯 Exam Preparation Assistant:** Generate mock tests, key point summaries, and revision plans tailored to the user's difficulty level.
*   **🦙 Llama 3 Integration:** Powered by advanced local LLMs for accurate and nuanced educational support.
*   **💻 Streamlit Web Interface:** A highly professional, responsive, NotebookLM-inspired frontend.

---

## 🧠 System Architecture

The project relies on a robust **Retrieval-Augmented Generation (RAG)** pipeline:

1.  **PDF Upload:** The user uploads a document via the frontend.
2.  **PDF Parsing:** `PyMuPDF` extracts the raw text page by page.
3.  **Text Cleaning:** The text is sanitized (removal of consecutive spaces, fixing line breaks).
4.  **Chunking:** `LangChain` splits the text into semantic chunks while retaining page metadata.
5.  **Embedding Generation:** `SentenceTransformers` (`all-MiniLM-L6-v2`) converts text chunks into dense vector representations.
6.  **FAISS Vector Store:** Vectors are indexed and stored locally using `FAISS` for ultra-fast similarity search.
7.  **Retrieval:** When a user asks a question or requests a feature, the system queries FAISS to retrieve the top-K most relevant chunks.
8.  **Prompt Construction:** The retrieved context, combined with specific educational instructions, is formatted into a precise prompt.
9.  **Llama 3 Generation:** `Ollama` runs the Llama 3 model locally to generate the final response.
10. **Response Delivery:** The backend formats the answer (and sources) and sends it to the Streamlit UI.

---

## 🛠️ Technology Stack

*   **Backend:** FastAPI, Python 3.10+, SQLAlchemy, SQLite, JWT Authentication
*   **Frontend:** Streamlit, Custom CSS
*   **AI & NLP:** Ollama, Llama 3, LangChain, Sentence Transformers
*   **Vector Database:** FAISS (Facebook AI Similarity Search)
*   **Document Processing:** PyMuPDF (`fitz`)

---

## 📁 Project Structure

```text
educational_assistant/
│
├── app/                        # Main FastAPI Backend Application
│   ├── core/                   # Core configuration and logging
│   │   ├── config.py           # Environment variables and app settings
│   │   ├── logger.py           # Custom logging configuration
│   │   └── security.py         # JWT token handling and password hashing
│   ├── db/                     # Database Models and Setup
│   │   ├── database.py         # SQLAlchemy engine and session management
│   │   └── models.py           # SQLite Table definitions (Users, Docs, Chats, Features)
│   ├── models/                 # Pydantic Schemas
│   │   └── schemas.py          # Request/Response validation models
│   ├── routers/                # API Endpoints
│   │   ├── auth.py             # Login, registration, profile routes
│   │   ├── chat.py             # RAG Q&A and chat history endpoints
│   │   ├── documents.py        # PDF upload, listing, and deletion
│   │   └── features.py         # Summaries, quizzes, flashcards, exam prep endpoints
│   └── services/               # Core Business Logic and AI Pipeline
│       ├── chunker.py          # Text chunking logic (LangChain)
│       ├── embedder.py         # SentenceTransformer embedding generation
│       ├── features_generator.py # Logic for parsing LLM feature outputs
│       ├── llm_engine.py       # Ollama LLM integration (Streaming & Batch)
│       ├── pdf_parser.py       # PyMuPDF text extraction
│       ├── prompt_builder.py   # System prompts and instruction formatting
│       ├── retriever.py        # Context retrieval logic
│       ├── text_cleaner.py     # Text sanitization
│       └── vector_store.py     # FAISS index building and querying
│
├── uploads/                    # (Ignored) Raw PDF files stored here
├── vectorstore/                # (Ignored) FAISS indexes and chunk pickles stored here
├── venv/                       # (Ignored) Python Virtual Environment
│
├── .env                        # Environment variables
├── .env.example                # Template for environment variables
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
└── streamlit_app.py            # Main Streamlit Frontend Application
```

---

## ⚙️ Installation Guide

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/educational_assistant.git
cd educational_assistant
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Install and configure Ollama
1. Download and install Ollama from [ollama.com](https://ollama.com/).
2. Open a terminal and pull the Llama 3 model:
```bash
ollama pull llama3
```

### 5. Configure environment variables
Copy the example environment file and update it if necessary:
```bash
cp .env.example .env
```

### 6. Launch the application

**Start the FastAPI Backend:**
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**Start the Streamlit Frontend (in a new terminal):**
```bash
python -m streamlit run streamlit_app.py
```

---

## 📖 Usage Guide

1. **Authentication:** Open `http://localhost:8501`. Create an account or log in.
2. **Upload PDFs:** Use the left sidebar to drag and drop your course PDFs. They will be indexed automatically.
3. **Chat:** Type a question in the main chat bar at the bottom. The AI will answer based on your documents and cite the exact page.
4. **Tools:** Use the sidebar navigation ("Tools") to switch to different modes:
   - **Summary:** Select a document and detail level, then click generate.
   - **Quiz:** Configure the number of questions, difficulty, and type. Take the interactive quiz and submit for grading.
   - **Flashcards:** Generate study cards. Click to reveal answers and navigate through the deck.
   - **Exam Prep:** Generate mock exams, revision plans, and key topics.

---

## 📸 Screenshots

### Home Page / Dashboard
> *(Add screenshot showing the main interface after login, sidebar, and welcome screen)*
[Insert Screenshot Here]

### Chat Interface with RAG Citations
> *(Add screenshot showing a chat interaction with source chips under the AI's response)*
[Insert Screenshot Here]

### Interactive Quiz Generator
> *(Add screenshot showing the quiz interface, radio buttons, and the graded score card)*
[Insert Screenshot Here]

### Study Flashcards
> *(Add screenshot showing the flashcard UI with the "Reveal" button)*
[Insert Screenshot Here]

---

## 🎥 Demonstration

*Add a link to a YouTube video demonstrating the project in action, or embed a GIF showing the PDF upload and chat process.*

[Link to Demo Video]

---

## 🔮 Future Improvements

*   **Multi-modal support:** Add support for extracting data from images, graphs, and charts within PDFs using Vision models.
*   **Agentic Workflows:** Implement a sub-agent to automatically scrape web resources to supplement PDF content when answers are insufficient.
*   **Spaced Repetition:** Integrate an Anki-style spaced repetition algorithm for the flashcards to track long-term retention.
*   **Cloud Deployment:** Containerize the application with Docker and deploy the backend to AWS/GCP, scaling the FAISS database with a dedicated vector DB like Pinecone or Milvus.

---

## 👨‍💻 Author

**[Your Name / Amal Benghnya]**
*Final Year Engineering Student*
* [GitHub](https://github.com/yourusername)
* [LinkedIn](https://linkedin.com/in/yourprofile)

*This project was developed as a comprehensive academic demonstration of modern AI and full-stack engineering principles.*
