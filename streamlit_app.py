"""
EduAI Assistant — Premium AI Educational Platform
Professional, dynamic, interactive interface.
Auto-indexing on upload, instant chat, full tool suite.
"""

import streamlit as st
import requests
import time
import json
import re

API_URL = "http://localhost:8000"

# ═══════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="EduAI Assistant – Intelligent Learning Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════
# GLOBAL CSS — Premium Dark Design
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Base ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: 'Inter', system-ui, sans-serif !important;
    background-color: #080d16 !important;
    color: #dde6f0 !important;
    margin: 0; padding: 0;
}

/* ── Hide Streamlit Chrome ── */
#MainMenu, footer, header, .stDeployButton { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }

/* ── Force sidebar ALWAYS open, hide collapse button ── */
[data-testid="collapsedControl"] { display: none !important; }
button[kind="header"] { display: none !important; }
.css-1lcbmhc, .css-1d391kg { display: block !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1424 0%, #0a1020 100%) !important;
    border-right: 1px solid #1a2840 !important;
    width: 310px !important;
    min-width: 310px !important;
    transform: translateX(0px) !important;
    visibility: visible !important;
    display: block !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
}
section[data-testid="stSidebar"] * { color: #dde6f0 !important; }

/* ── Main content ── */
.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── SIDEBAR COMPONENTS ── */
.sb-header {
    padding: 20px 18px 14px;
    border-bottom: 1px solid #1a2840;
    display: flex;
    align-items: center;
    gap: 10px;
}
.sb-logo {
    font-size: 1.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.sb-status-on {
    font-size: 0.7rem;
    padding: 3px 10px;
    border-radius: 20px;
    background: #052010;
    border: 1px solid #16a34a;
    color: #4ade80 !important;
    font-weight: 600;
    margin-left: auto;
}
.sb-status-off {
    font-size: 0.7rem;
    padding: 3px 10px;
    border-radius: 20px;
    background: #1c0707;
    border: 1px solid #dc2626;
    color: #f87171 !important;
    font-weight: 600;
    margin-left: auto;
}
.sb-user-card {
    margin: 12px 16px;
    padding: 12px 14px;
    background: #111c2e;
    border: 1px solid #1a2840;
    border-radius: 12px;
}
.sb-user-role {
    font-size: 0.65rem !important;
    color: #4b6080 !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 2px;
}
.sb-user-name {
    font-weight: 700 !important;
    color: #f0f6ff !important;
    font-size: 0.92rem !important;
}
.sb-user-email {
    color: #60a5fa !important;
    font-size: 0.73rem !important;
    font-family: 'JetBrains Mono', monospace !important;
    margin-top: 1px;
}
.sb-section-label {
    padding: 14px 18px 6px;
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #3a5070 !important;
    border-top: 1px solid #1a2840;
    margin-top: 6px;
}
.doc-card {
    margin: 4px 10px;
    padding: 10px 12px;
    background: #111c2e;
    border: 1px solid #1a2840;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.2s ease;
}
.doc-card:hover { border-color: #2563eb; background: #0f1928; }
.doc-card.active { border-color: #3b82f6; background: #0c1829; box-shadow: 0 0 0 1px #1e40af44; }
.doc-card-name {
    font-size: 0.83rem;
    font-weight: 600;
    color: #e2e8f0 !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 200px;
}
.doc-card-meta { font-size: 0.7rem; color: #4b6080 !important; margin-top: 2px; font-family: 'JetBrains Mono', monospace; }

/* ── TOP BAR ── */
.topbar {
    background: #0d1424;
    border-bottom: 1px solid #1a2840;
    padding: 12px 28px;
    display: flex;
    align-items: center;
    gap: 14px;
    position: sticky;
    top: 0;
    z-index: 100;
}
.topbar-doc {
    background: #111c2e;
    border: 1px solid #1a2840;
    border-radius: 20px;
    padding: 5px 16px;
    font-size: 0.8rem;
    color: #93c5fd !important;
    font-family: 'JetBrains Mono', monospace;
    max-width: 300px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.topbar-title {
    font-size: 0.9rem;
    font-weight: 600;
    color: #e2e8f0 !important;
}

/* ── TOOL TABS BAR ── */
.tool-bar {
    display: flex;
    gap: 6px;
    padding: 10px 28px;
    background: #0a1020;
    border-bottom: 1px solid #1a2840;
    flex-wrap: wrap;
}

/* ── CHAT AREA ── */
.chat-scroll {
    height: calc(100vh - 230px);
    overflow-y: auto;
    padding: 20px 28px;
    display: flex;
    flex-direction: column;
    gap: 14px;
    scroll-behavior: smooth;
}
.msg-user {
    align-self: flex-end;
    background: linear-gradient(135deg, #1d4ed8, #2563eb);
    color: #fff !important;
    padding: 12px 18px;
    border-radius: 20px 20px 4px 20px;
    max-width: 68%;
    font-size: 0.92rem;
    line-height: 1.65;
    box-shadow: 0 4px 24px rgba(37,99,235,0.28);
}
.msg-ai {
    align-self: flex-start;
    background: #111c2e;
    border: 1px solid #1a2840;
    color: #dde6f0 !important;
    padding: 14px 18px;
    border-radius: 4px 20px 20px 20px;
    max-width: 80%;
    font-size: 0.92rem;
    line-height: 1.75;
    box-shadow: 0 2px 12px rgba(0,0,0,0.2);
}
.msg-ai strong { color: #60a5fa !important; }
.msg-ai code {
    background: #0a1525;
    color: #7dd3fc !important;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.86em;
}
.msg-ai h1,.msg-ai h2,.msg-ai h3 { color: #93c5fd !important; }
.msg-ai ul,.msg-ai ol { padding-left: 18px; }
.msg-ai li { margin: 3px 0; }
.msg-ai pre {
    background: #0a1525;
    border: 1px solid #1a2840;
    border-radius: 8px;
    padding: 12px;
    overflow-x: auto;
}
.ai-avatar {
    width: 28px; height: 28px;
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    flex-shrink: 0;
    margin-right: 6px;
    vertical-align: middle;
}
.sources-strip {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid #1a2840;
}
.src-chip {
    background: #0a1525;
    border: 1px solid #1e3a5f;
    border-radius: 14px;
    padding: 2px 10px;
    font-size: 0.7rem;
    color: #60a5fa !important;
    font-family: 'JetBrains Mono', monospace;
}

/* ── CHAT INPUT ── */
.chat-input-bar {
    position: sticky;
    bottom: 0;
    background: #0a1020;
    border-top: 1px solid #1a2840;
    padding: 12px 28px;
}

/* ── WELCOME / EMPTY STATE ── */
.welcome-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 24px;
    text-align: center;
}
.welcome-icon { font-size: 3.5rem; margin-bottom: 16px; }
.welcome-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #e2e8f0 !important;
    margin-bottom: 8px;
}
.welcome-sub { font-size: 0.9rem; color: #4b6080 !important; max-width: 380px; line-height: 1.6; }
.suggestion-grid { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-top: 24px; max-width: 480px; }
.sugg-btn {
    background: #111c2e;
    border: 1px solid #1a2840;
    border-radius: 20px;
    padding: 8px 16px;
    font-size: 0.8rem;
    color: #93c5fd !important;
    cursor: pointer;
    transition: all 0.2s;
}
.sugg-btn:hover { background: #1a2840; border-color: #3b82f6; color: #f0f6ff !important; }

/* ── UPLOAD STATUS ── */
.upload-progress {
    background: #0f1928;
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: 10px 14px;
    margin: 6px 10px;
    font-size: 0.8rem;
    color: #93c5fd !important;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ── FEATURE PANELS ── */
.panel-wrap {
    padding: 20px 28px;
    height: calc(100vh - 165px);
    overflow-y: auto;
}
.panel-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #f0f6ff !important;
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 18px;
    padding-bottom: 12px;
    border-bottom: 1px solid #1a2840;
}
.panel-section-label {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #4b6080 !important;
    margin: 16px 0 8px;
}
.content-block {
    background: #111c2e;
    border: 1px solid #1a2840;
    border-left: 3px solid #2563eb;
    border-radius: 0 10px 10px 0;
    padding: 16px 20px;
    font-size: 0.91rem;
    line-height: 1.8;
    color: #dde6f0 !important;
    white-space: pre-wrap;
}

/* ── QUIZ ── */
.quiz-card {
    background: #111c2e;
    border: 1px solid #1a2840;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 14px;
    transition: border-color 0.2s;
}
.quiz-card:hover { border-color: #2563eb44; }
.quiz-q { font-weight: 600; font-size: 0.94rem; color: #f0f6ff !important; margin-bottom: 12px; }
.quiz-correct { border-color: #16a34a !important; background: #04150a !important; }
.quiz-wrong   { border-color: #dc2626 !important; background: #150404 !important; }
.quiz-expl {
    margin-top: 10px;
    font-size: 0.81rem;
    color: #4b6080 !important;
    padding-left: 12px;
    border-left: 2px solid #1a2840;
    font-style: italic;
    line-height: 1.6;
}
.score-card {
    text-align: center;
    background: #111c2e;
    border: 1px solid #1a2840;
    border-radius: 16px;
    padding: 36px;
    margin-bottom: 20px;
}
.score-num { font-size: 3.5rem; font-weight: 800; font-family: 'JetBrains Mono'; color: #60a5fa !important; }
.score-label { font-size: 0.9rem; color: #4b6080 !important; margin-top: 6px; }

/* ── FLASHCARDS ── */
.fc-front {
    background: linear-gradient(135deg, #0e2444 0%, #1a3a6e 100%);
    border: 1px solid #2563eb;
    border-radius: 16px;
    padding: 40px 28px;
    text-align: center;
    min-height: 160px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.05rem;
    font-weight: 600;
    color: #f0f6ff !important;
    line-height: 1.6;
    box-shadow: 0 8px 32px rgba(37,99,235,0.2);
}
.fc-back {
    background: #111c2e;
    border: 1px solid #1a2840;
    border-radius: 16px;
    padding: 28px;
    text-align: center;
    min-height: 110px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.93rem;
    color: #93c5fd !important;
    line-height: 1.7;
    margin-top: 12px;
}
.fc-counter { text-align: center; color: #4b6080 !important; font-size: 0.8rem; margin-bottom: 10px; }

/* ── METRICS ROW ── */
.metrics-row { display: flex; gap: 10px; margin: 14px 0; }
.metric-card {
    flex: 1;
    background: #111c2e;
    border: 1px solid #1a2840;
    border-radius: 10px;
    padding: 14px 10px;
    text-align: center;
}
.metric-val { font-size: 1.5rem; font-weight: 800; color: #60a5fa !important; font-family: 'JetBrains Mono'; }
.metric-lbl { font-size: 0.65rem; color: #4b6080 !important; text-transform: uppercase; letter-spacing: 0.07em; margin-top: 3px; }

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #111c2e !important;
    border: 1px solid #1a2840 !important;
    border-radius: 10px !important;
    color: #dde6f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.91rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.1) !important;
    outline: none !important;
}
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: #111c2e !important;
    border: 1px solid #1a2840 !important;
    border-radius: 10px !important;
    color: #dde6f0 !important;
}

/* ── BUTTONS ── */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    background: #111c2e !important;
    border: 1px solid #1a2840 !important;
    color: #93c5fd !important;
    transition: all 0.18s ease !important;
    font-family: 'Inter', sans-serif !important;
}
.stButton > button:hover {
    background: #1a2840 !important;
    border-color: #3b82f6 !important;
    color: #f0f6ff !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(59,130,246,0.18) !important;
}
.stButton > button:active { transform: translateY(0) !important; }
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    border-color: #3b82f6 !important;
    color: #fff !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
    box-shadow: 0 4px 20px rgba(59,130,246,0.35) !important;
}

/* ── SIDEBAR BUTTONS ── */
section[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    text-align: left !important;
    background: transparent !important;
    border: none !important;
    padding: 8px 12px !important;
    font-size: 0.85rem !important;
    color: #8ba3c0 !important;
    border-radius: 8px !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #1a2840 !important;
    color: #f0f6ff !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ── ALERTS ── */
.stSuccess { background: #031a0d !important; border: 1px solid #15803d !important; border-radius: 8px !important; color: #4ade80 !important; }
.stError   { background: #150404 !important; border: 1px solid #b91c1c !important; border-radius: 8px !important; }
.stInfo    { background: #07142a !important; border: 1px solid #1d4ed8 !important; border-radius: 8px !important; }
.stWarning { background: #14100a !important; border: 1px solid #b45309 !important; border-radius: 8px !important; }

/* ── TABS ── */
button[data-baseweb="tab"] {
    font-size: 0.83rem !important;
    font-weight: 600 !important;
    color: #4b6080 !important;
    background: transparent !important;
    border: none !important;
    padding: 6px 14px !important;
    border-radius: 20px !important;
    transition: all 0.15s !important;
}
button[data-baseweb="tab"]:hover { background: #111c2e !important; color: #93c5fd !important; }
button[data-baseweb="tab"][aria-selected="true"] {
    color: #60a5fa !important;
    background: #111c2e !important;
    box-shadow: none !important;
}
[data-baseweb="tab-highlight"] { background: #2563eb !important; height: 2px !important; }
[data-baseweb="tab-border"] { border-color: #1a2840 !important; }

/* ── PROGRESS ── */
.stProgress > div > div > div { background: linear-gradient(90deg, #2563eb, #7c3aed) !important; border-radius: 4px !important; }

/* ── SPINNER ── */
.stSpinner > div { border-top-color: #3b82f6 !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #1a2840; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #2a3f5f; }

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] > div {
    background: #111c2e !important;
    border: 2px dashed #1a2840 !important;
    border-radius: 12px !important;
    transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"] > div:hover { border-color: #2563eb !important; }

/* ── RADIO ── */
.stRadio > div { gap: 6px !important; }
.stRadio > div > label {
    background: #111c2e !important;
    border: 1px solid #1a2840 !important;
    border-radius: 8px !important;
    padding: 6px 12px !important;
    cursor: pointer !important;
    transition: all 0.15s !important;
    font-size: 0.84rem !important;
}
.stRadio > div > label:hover { border-color: #3b82f6 !important; }

/* ── SLIDER ── */
.stSlider > div > div > div { background: #2563eb !important; }

/* ── CHECKBOX ── */
.stCheckbox > label > span { background: #2563eb !important; border-color: #2563eb !important; }

/* ── Typing animation ── */
@keyframes typing {
    0%, 100% { opacity: 0.2; transform: scale(0.8); }
    50% { opacity: 1; transform: scale(1.1); }
}
.typing-dots span {
    display: inline-block;
    width: 7px; height: 7px;
    background: #3b82f6;
    border-radius: 50%;
    margin: 0 2px;
    animation: typing 1.2s ease infinite;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

/* ── Pulse animation ── */
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 0 0 rgba(37,99,235,0); }
    50% { box-shadow: 0 0 0 4px rgba(37,99,235,0.15); }
}
.uploading { animation: pulse-glow 1.5s ease infinite; }

/* ── Divider ── */
hr { border-color: #1a2840 !important; margin: 10px 0 !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════
_defaults = {
    "token": None,
    "user_info": None,
    "docs": {},
    "active_doc_id": "all",
    "chat_history": [],
    "session_id": f"s_{int(time.time())}",
    "quiz_data": None,
    "quiz_answers": {},
    "quiz_submitted": False,
    "flashcards": [],
    "fc_index": 0,
    "fc_reveal": False,
    "summary_cache": {},
    "exam_cache": {},
    "active_tool": "chat",          # chat | summary | quiz | flashcards | exam
    "pending_question": None,
    "uploaded_ids": set(),
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ═══════════════════════════════════════════════════════════════════
# API HELPERS
# ═══════════════════════════════════════════════════════════════════
def hdrs():
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}

def api_alive():
    try:
        return requests.get(f"{API_URL}/", timeout=2).status_code == 200
    except:
        return False

def login_user(email, pwd):
    try:
        r = requests.post(f"{API_URL}/auth/login",
                          json={"email": email, "password": pwd}, timeout=10)
        if r.ok:
            st.session_state.token = r.json()["access_token"]
            return True, ""
        return False, r.json().get("detail", "Invalid credentials")
    except Exception as e:
        return False, str(e)

def register_user(name, email, pwd):
    try:
        r = requests.post(f"{API_URL}/auth/register",
                          json={"name": name, "email": email, "password": pwd}, timeout=10)
        return r.ok, r.json().get("detail", "Error")
    except Exception as e:
        return False, str(e)

def fetch_profile():
    try:
        r = requests.get(f"{API_URL}/auth/me", headers=hdrs(), timeout=5)
        if r.ok:
            st.session_state.user_info = r.json()
    except:
        pass

def fetch_docs():
    try:
        r = requests.get(f"{API_URL}/documents", headers=hdrs(), timeout=10)
        if r.ok:
            st.session_state.docs = {
                d["doc_id"]: {
                    "name": d["filename"],
                    "size": d["file_size"],
                    "pages": d["num_pages"],
                    "chunks": d["num_chunks"],
                    "date": d["upload_date"]
                }
                for d in r.json()
            }
    except:
        pass

def upload_pdf(file_bytes, filename):
    try:
        r = requests.post(
            f"{API_URL}/documents/upload",
            files={"file": (filename, file_bytes, "application/pdf")},
            headers=hdrs(),
            timeout=300,
        )
        return (True, r.json()) if r.ok else (False, r.json().get("detail", r.text))
    except Exception as e:
        return False, str(e)

def delete_doc(doc_id):
    try:
        r = requests.delete(f"{API_URL}/documents/{doc_id}", headers=hdrs(), timeout=15)
        return r.ok
    except:
        return False

def ask_rag(doc_id, question, session_id, top_k=6):
    try:
        r = requests.post(
            f"{API_URL}/chat/ask",
            json={"doc_id": doc_id, "question": question,
                  "session_id": session_id, "top_k": top_k},
            headers=hdrs(),
            timeout=120,
        )
        if r.ok:
            return r.json()
        return {"answer": f"⚠️ Server error ({r.status_code})", "sources": []}
    except Exception as e:
        return {"answer": f"⚠️ Connection failed: {e}", "sources": []}

def clear_history(sid):
    try:
        requests.post(f"{API_URL}/chat/clear/{sid}", headers=hdrs(), timeout=5)
    except:
        pass

def get_summary(doc_id, level):
    try:
        r = requests.post(f"{API_URL}/features/summarize",
                          json={"doc_id": doc_id, "detail_level": level},
                          headers=hdrs(), timeout=180)
        if r.ok:
            d = r.json()
            return True, d.get("summary", ""), d.get("id")
        return False, r.text, None
    except Exception as e:
        return False, str(e), None

def get_quiz(doc_id, n, diff, qtype):
    try:
        r = requests.post(f"{API_URL}/features/quiz",
                          json={"doc_id": doc_id, "num_questions": n,
                                "difficulty": diff, "question_type": qtype},
                          headers=hdrs(), timeout=180)
        return (True, r.json()) if r.ok else (False, r.text)
    except Exception as e:
        return False, str(e)

def get_flashcards(doc_id):
    try:
        r = requests.post(f"{API_URL}/features/flashcards",
                          json={"doc_id": doc_id},
                          headers=hdrs(), timeout=180)
        return (True, r.json()) if r.ok else (False, r.text)
    except Exception as e:
        return False, str(e)

def get_exam(doc_id, prep_type, difficulty):
    try:
        r = requests.post(f"{API_URL}/features/exam-prep",
                          json={"doc_id": doc_id, "prep_type": prep_type,
                                "difficulty": difficulty},
                          headers=hdrs(), timeout=180)
        if r.ok:
            d = r.json()
            return True, d.get("content", ""), d.get("id")
        return False, r.text, None
    except Exception as e:
        return False, str(e), None

def active_doc_name():
    if st.session_state.active_doc_id == "all":
        return "All Documents"
    doc = st.session_state.docs.get(st.session_state.active_doc_id)
    return doc["name"] if doc else "Unknown"

def fmt_size(b):
    if b < 1024:
        return f"{b}B"
    if b < 1024**2:
        return f"{b/1024:.1f}KB"
    return f"{b/1024**2:.1f}MB"

def render_markdown(text):
    """Simple markdown to HTML for chat bubbles."""
    import html
    text = html.escape(text)
    # Bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    # Inline code
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    # Headers
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    # Lists
    text = re.sub(r'^\- (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'^(\d+)\. (.+)$', r'<li>\2</li>', text, flags=re.MULTILINE)
    # Newlines
    text = text.replace('\n', '<br>')
    return text


# ═══════════════════════════════════════════════════════════════════
# ── AUTH PAGE ──
# ═══════════════════════════════════════════════════════════════════
if not st.session_state.token:
    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center; margin-bottom:36px;">
            <div style="font-size:4rem; margin-bottom:12px;">🎓</div>
            <h1 style="font-size:2rem; font-weight:800; color:#f0f6ff; margin:0 0 6px;">EduAI Assistant</h1>
            <p style="color:#4b6080; font-size:0.92rem; margin:0;">
                Your intelligent AI-powered study companion
            </p>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_reg = st.tabs(["🔑 Sign In", "✨ Create Account"])

        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("login_form", clear_on_submit=False):
                email_in = st.text_input("Email address", placeholder="your@email.com")
                pwd_in   = st.text_input("Password", type="password", placeholder="••••••••")
                st.markdown("<br>", unsafe_allow_html=True)
                login_btn = st.form_submit_button("Sign In →", use_container_width=True, type="primary")
            if login_btn:
                if email_in and pwd_in:
                    with st.spinner("Authenticating..."):
                        ok, msg = login_user(email_in.strip(), pwd_in)
                    if ok:
                        fetch_profile()
                        fetch_docs()
                        st.success("✅ Login successful!")
                        time.sleep(0.4)
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
                else:
                    st.warning("Please fill in all fields.")

        with tab_reg:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("register_form", clear_on_submit=False):
                name_up  = st.text_input("Full name", placeholder="Your Name")
                email_up = st.text_input("Email", placeholder="student@email.com")
                pwd_up   = st.text_input("Password (min. 6 chars)", type="password")
                st.markdown("<br>", unsafe_allow_html=True)
                reg_btn = st.form_submit_button("Create Account →", use_container_width=True, type="primary")
            if reg_btn:
                if name_up and email_up and pwd_up:
                    if len(pwd_up) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        with st.spinner("Creating account..."):
                            ok, msg = register_user(name_up.strip(), email_up.strip(), pwd_up)
                        if ok:
                            st.success("✅ Account created! Please sign in.")
                        else:
                            st.error(f"❌ {msg}")
                else:
                    st.warning("All fields are required.")
    st.stop()


# ═══════════════════════════════════════════════════════════════════
# INIT LOGGED-IN STATE
# ═══════════════════════════════════════════════════════════════════
if not st.session_state.user_info:
    fetch_profile()
    fetch_docs()


# ═══════════════════════════════════════════════════════════════════
# ── SIDEBAR ──
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:
    alive = api_alive()
    status_html = (
        '<span class="sb-status-on">● Online</span>' if alive
        else '<span class="sb-status-off">● Offline</span>'
    )
    st.markdown(f"""
    <div class="sb-header">
        <span class="sb-logo">🎓 EduAI</span>
        {status_html}
    </div>
    """, unsafe_allow_html=True)

    if not alive:
        st.error("⚠️ Backend is unreachable on port 8000. Please ensure the server is running.")
        st.stop()

    # User card
    u = st.session_state.user_info or {}
    if u:
        st.markdown(f"""
        <div class="sb-user-card">
            <div class="sb-user-role">Student</div>
            <div class="sb-user-name">{u.get('name','User')}</div>
            <div class="sb-user-email">{u.get('email','')}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── UPLOAD SECTION ──
    st.markdown('<div class="sb-section-label">📂 Upload PDF</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Drop PDF here",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    # Auto-index on new upload
    if uploaded:
        for uf in uploaded:
            file_key = f"{uf.name}_{uf.size}"
            if file_key not in st.session_state.uploaded_ids:
                with st.spinner(f"📥 Indexing **{uf.name}**…"):
                    ok, result = upload_pdf(uf.read(), uf.name)
                if ok:
                    st.session_state.uploaded_ids.add(file_key)
                    fetch_docs()
                    # Auto-select the new document
                    st.session_state.active_doc_id = result.get("doc_id", "all")
                    st.success(f"✅ **{uf.name}** indexed — {result.get('num_chunks', 0)} chunks ready!")
                    time.sleep(0.8)
                    st.rerun()
                else:
                    st.error(f"❌ Upload failed: {result}")

    # ── SOURCES SECTION ──
    docs = st.session_state.docs
    st.markdown('<div class="sb-section-label">📚 Your Sources</div>', unsafe_allow_html=True)

    if not docs:
        st.markdown("""
        <div style="padding:14px 16px; text-align:center; color:#3a5070; font-size:0.8rem; line-height:1.6;">
            📄 No documents yet.<br>Upload a PDF to get started.
        </div>
        """, unsafe_allow_html=True)
    else:
        # "All docs" option
        is_all = st.session_state.active_doc_id == "all"
        if st.button(
            f"{'✦ ' if is_all else '  '}🌐 All Documents ({len(docs)})",
            key="btn_all",
            use_container_width=True
        ):
            st.session_state.active_doc_id = "all"
            st.rerun()

        for did, info in docs.items():
            is_active = st.session_state.active_doc_id == did
            emoji = "✦ " if is_active else "  "
            name_short = info["name"][:30] + "…" if len(info["name"]) > 30 else info["name"]
            if st.button(
                f"{emoji}📄 {name_short}",
                key=f"doc_{did}",
                use_container_width=True
            ):
                st.session_state.active_doc_id = did
                st.rerun()

    # ── NAVIGATION ──
    st.markdown('<div class="sb-section-label">🧭 Tools</div>', unsafe_allow_html=True)

    tools = [
        ("chat", "💬 Chat"),
        ("summary", "📝 Summary"),
        ("quiz", "🧪 Quiz"),
        ("flashcards", "🃏 Flashcards"),
        ("exam", "🎯 Exam Prep"),
    ]
    for tool_id, label in tools:
        is_active = st.session_state.active_tool == tool_id
        btn_label = f"{'▶ ' if is_active else '   '}{label}"
        if st.button(btn_label, key=f"nav_{tool_id}", use_container_width=True):
            st.session_state.active_tool = tool_id
            st.rerun()

    st.markdown('<div class="sb-section-label">⚙️ Account</div>', unsafe_allow_html=True)
    col_r, col_l = st.columns(2)
    with col_r:
        if st.button("🔄 Refresh", use_container_width=True):
            fetch_docs()
            st.rerun()
    with col_l:
        if st.button("🚪 Logout", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()


# ═══════════════════════════════════════════════════════════════════
# ── MAIN AREA ──
# ═══════════════════════════════════════════════════════════════════
docs = st.session_state.docs
tool = st.session_state.active_tool
active_id = st.session_state.active_doc_id
doc_name = active_doc_name()
has_docs = bool(docs)

# ── TOP BAR ──
st.markdown(f"""
<div class="topbar">
    <span class="topbar-title">AI-Powered Educational Assistant</span>
    <span class="topbar-doc">📄 {doc_name}</span>
    <span style="margin-left:auto; font-size:0.75rem; color:#3a5070;">
        {len(docs)} source{'s' if len(docs) != 1 else ''} · Session active
    </span>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# ── CHAT PANEL ──
# ═══════════════════════════════════════════════════════════════════
if tool == "chat":

    chat_container = st.container()

    with chat_container:
        if not st.session_state.chat_history:
            # Welcome state with suggestions
            suggestions = [
                "📖 Summarize this document",
                "🔑 What are the key concepts?",
                "💡 Explain the main ideas",
                "❓ Generate a quiz question",
                "🎯 What should I focus on?",
                "📊 List the important formulas",
            ]
            st.markdown("""
            <div class="welcome-wrap">
                <div class="welcome-icon">🤖</div>
                <div class="welcome-title">Ask me anything about your documents</div>
                <div class="welcome-sub">
                    Upload a PDF using the sidebar, then start asking questions.
                    I'll answer based on the content of your documents.
                </div>
            </div>
            """, unsafe_allow_html=True)

            if has_docs:
                st.markdown("""
                <div style="text-align:center; margin-top:8px; color:#4b6080; font-size:0.8rem;">
                    Try one of these:
                </div>
                """, unsafe_allow_html=True)
                cols = st.columns(3)
                for i, s in enumerate(suggestions):
                    with cols[i % 3]:
                        if st.button(s, key=f"sugg_{i}", use_container_width=True):
                            st.session_state.pending_question = s.split(" ", 1)[1]
                            st.rerun()
        else:
            # Render chat messages
            msgs_html = '<div class="chat-scroll" id="chat-bottom">'
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    msgs_html += f'<div class="msg-user">{render_markdown(msg["content"])}</div>'
                else:
                    content_html = render_markdown(msg["content"])
                    sources = msg.get("sources", [])
                    src_html = ""
                    if sources:
                        src_html = '<div class="sources-strip">'
                        seen = set()
                        for s in sources[:4]:
                            label = f'📄 {s["file"]} · p.{s["page"]}'
                            if label not in seen:
                                src_html += f'<span class="src-chip">{label}</span>'
                                seen.add(label)
                        src_html += '</div>'
                    msgs_html += f'<div class="msg-ai"><span class="ai-avatar">🤖</span>{content_html}{src_html}</div>'
            msgs_html += '</div>'
            st.markdown(msgs_html, unsafe_allow_html=True)

    # Input bar
    st.markdown('<div class="chat-input-bar">', unsafe_allow_html=True)
    input_cols = st.columns([10, 1, 1])
    with input_cols[0]:
        question = st.text_input(
            "question",
            placeholder="Ask a question about your documents… (Enter to send)",
            label_visibility="collapsed",
            key="chat_input",
            value=st.session_state.pending_question or "",
        )
    with input_cols[1]:
        send_btn = st.button("Send", key="send_btn", type="primary", use_container_width=True)
    with input_cols[2]:
        if st.button("🗑️", key="clear_btn", use_container_width=True, help="Clear chat"):
            st.session_state.chat_history = []
            clear_history(st.session_state.session_id)
            st.session_state.session_id = f"s_{int(time.time())}"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Handle send
    if st.session_state.pending_question:
        question = st.session_state.pending_question
        st.session_state.pending_question = None
        send_btn = True

    if send_btn and question and question.strip():
        if not has_docs:
            st.warning("⚠️ Please upload at least one PDF document first.")
        else:
            # Append user message
            st.session_state.chat_history.append({
                "role": "user",
                "content": question.strip()
            })

            # Get AI response
            with st.spinner("🤖 Thinking…"):
                result = ask_rag(
                    active_id,
                    question.strip(),
                    st.session_state.session_id
                )

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": result.get("answer", "No response received."),
                "sources": result.get("sources", [])
            })
            st.rerun()


# ═══════════════════════════════════════════════════════════════════
# ── SUMMARY PANEL ──
# ═══════════════════════════════════════════════════════════════════
elif tool == "summary":
    st.markdown('<div class="panel-wrap">', unsafe_allow_html=True)
    st.markdown("""
    <div class="panel-title">
        📝 <span>Document Summary</span>
    </div>
    """, unsafe_allow_html=True)

    if not has_docs:
        st.info("📄 Upload a PDF document to generate summaries.")
    else:
        col1, col2 = st.columns([2, 1])
        with col1:
            if len(docs) > 1:
                doc_opts = {v["name"]: k for k, v in docs.items()}
                chosen = st.selectbox("Select document", list(doc_opts.keys()), key="sum_doc")
                sum_doc_id = doc_opts[chosen]
            else:
                sum_doc_id = list(docs.keys())[0]
                st.markdown(f'<div class="panel-section-label">Document: {list(docs.values())[0]["name"]}</div>', unsafe_allow_html=True)

        with col2:
            level = st.radio("Detail level", ["brief", "standard", "detailed"],
                             horizontal=True, key="sum_level", index=1)

        cache_key = f"{sum_doc_id}_{level}"

        if st.button("✨ Generate Summary", type="primary", key="gen_sum"):
            with st.spinner("📝 Generating summary… this may take a moment"):
                ok, text, _ = get_summary(sum_doc_id, level)
            if ok:
                st.session_state.summary_cache[cache_key] = text
            else:
                st.error(f"❌ Error: {text}")

        if cache_key in st.session_state.summary_cache:
            txt = st.session_state.summary_cache[cache_key]
            st.markdown(f'<div class="content-block">{txt}</div>', unsafe_allow_html=True)
            st.download_button(
                "⬇️ Download Summary",
                data=txt,
                file_name=f"summary_{level}.txt",
                mime="text/plain",
                key="dl_sum"
            )

    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# ── QUIZ PANEL ──
# ═══════════════════════════════════════════════════════════════════
elif tool == "quiz":
    st.markdown('<div class="panel-wrap">', unsafe_allow_html=True)
    st.markdown("""
    <div class="panel-title">
        🧪 <span>Interactive Quiz</span>
    </div>
    """, unsafe_allow_html=True)

    if not has_docs:
        st.info("📄 Upload a PDF document to generate quizzes.")
    else:
        if st.session_state.quiz_data is None:
            # Config
            col1, col2, col3 = st.columns(3)
            with col1:
                if len(docs) > 1:
                    doc_opts = {v["name"]: k for k, v in docs.items()}
                    chosen = st.selectbox("Document", list(doc_opts.keys()), key="quiz_doc")
                    q_doc_id = doc_opts[chosen]
                else:
                    q_doc_id = list(docs.keys())[0]
                    st.markdown(f'<div class="panel-section-label">{list(docs.values())[0]["name"]}</div>', unsafe_allow_html=True)

            with col2:
                n_q = st.slider("Questions", 3, 15, 5, key="quiz_n")
            with col3:
                diff = st.radio("Difficulty", ["easy", "medium", "hard"],
                                horizontal=True, key="quiz_diff", index=1)

            qtype = st.radio("Type", ["multiple_choice", "true_false", "short_answer"],
                             horizontal=True, key="quiz_type")

            if st.button("🚀 Generate Quiz", type="primary", key="gen_quiz"):
                with st.spinner("🧪 Generating quiz questions…"):
                    ok, data = get_quiz(q_doc_id, n_q, diff, qtype)
                if ok:
                    questions = data.get("questions", [])
                    if questions:
                        st.session_state.quiz_data = questions
                        st.session_state.quiz_answers = {}
                        st.session_state.quiz_submitted = False
                        st.rerun()
                    else:
                        st.warning("No questions generated. Try a different document or settings.")
                else:
                    st.error(f"❌ Error: {data}")
        else:
            # Show quiz
            questions = st.session_state.quiz_data
            submitted = st.session_state.quiz_submitted

            if submitted:
                # Score
                correct = sum(
                    1 for i, q in enumerate(questions)
                    if str(st.session_state.quiz_answers.get(i, "")).strip().lower()
                    == str(q.get("correct_answer", "")).strip().lower()
                )
                pct = int(correct / len(questions) * 100) if questions else 0
                color = "#4ade80" if pct >= 70 else "#facc15" if pct >= 40 else "#f87171"
                st.markdown(f"""
                <div class="score-card">
                    <div class="score-num" style="color:{color} !important;">{pct}%</div>
                    <div class="score-label">{correct} / {len(questions)} correct</div>
                </div>
                """, unsafe_allow_html=True)

            for i, q in enumerate(questions):
                opts = q.get("options", [])
                ans = st.session_state.quiz_answers.get(i)
                correct_ans = str(q.get("correct_answer", "")).strip()

                card_cls = ""
                if submitted and ans is not None:
                    card_cls = "quiz-correct" if str(ans).strip().lower() == correct_ans.lower() else "quiz-wrong"

                st.markdown(f'<div class="quiz-card {card_cls}">', unsafe_allow_html=True)
                st.markdown(f'<div class="quiz-q">Q{i+1}. {q.get("question", "")}</div>', unsafe_allow_html=True)

                if opts:
                    if isinstance(opts, dict):
                        display_opts = [f"{k}) {v}" for k, v in opts.items()]
                    elif isinstance(opts, list):
                        display_opts = opts
                    else:
                        display_opts = []

                    chosen_full = st.radio(
                        f"q{i}",
                        display_opts,
                        key=f"qa_{i}",
                        label_visibility="collapsed",
                        disabled=submitted,
                        index=None
                    )
                    
                    # Extract the letter (e.g. 'A') or use the full choice
                    if chosen_full:
                        if isinstance(opts, dict) and ")" in chosen_full:
                            chosen = chosen_full.split(")")[0].strip()
                        else:
                            chosen = chosen_full
                    else:
                        chosen = None

                    if chosen != st.session_state.quiz_answers.get(i):
                        st.session_state.quiz_answers[i] = chosen
                else:
                    user_ans = st.text_input(
                        f"Your answer",
                        key=f"qa_{i}",
                        disabled=submitted,
                        label_visibility="visible"
                    )
                    st.session_state.quiz_answers[i] = user_ans

                if submitted:
                    icon = "✅" if str(ans or "").strip().lower() == correct_ans.lower() else "❌"
                    st.markdown(f'<div class="quiz-expl">{icon} Correct answer: <strong>{correct_ans}</strong><br>{q.get("explanation", "")}</div>', unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if not submitted:
                    if st.button("✅ Submit Answers", type="primary", key="submit_quiz", use_container_width=True):
                        st.session_state.quiz_submitted = True
                        st.rerun()
            with btn_col2:
                if st.button("🔄 New Quiz", key="reset_quiz", use_container_width=True):
                    st.session_state.quiz_data = None
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_submitted = False
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# ── FLASHCARDS PANEL ──
# ═══════════════════════════════════════════════════════════════════
elif tool == "flashcards":
    st.markdown('<div class="panel-wrap">', unsafe_allow_html=True)
    st.markdown("""
    <div class="panel-title">
        🃏 <span>Flashcards</span>
    </div>
    """, unsafe_allow_html=True)

    if not has_docs:
        st.info("📄 Upload a PDF document to generate flashcards.")
    else:
        flashcards = st.session_state.flashcards

        if not flashcards:
            if len(docs) > 1:
                doc_opts = {v["name"]: k for k, v in docs.items()}
                chosen = st.selectbox("Select document", list(doc_opts.keys()), key="fc_doc")
                fc_doc_id = doc_opts[chosen]
            else:
                fc_doc_id = list(docs.keys())[0]
                st.markdown(f'<div class="panel-section-label">{list(docs.values())[0]["name"]}</div>', unsafe_allow_html=True)

            if st.button("🃏 Generate Flashcards", type="primary", key="gen_fc"):
                with st.spinner("🃏 Generating flashcards…"):
                    ok, data = get_flashcards(fc_doc_id)
                if ok:
                    if isinstance(data, list):
                        cards = data
                    else:
                        cards = data.get("flashcards", [])
                        
                    if cards:
                        st.session_state.flashcards = cards
                        st.session_state.fc_index = 0
                        st.session_state.fc_reveal = False
                        st.rerun()
                    else:
                        st.warning("No flashcards generated.")
                else:
                    st.error(f"❌ Error: {data}")
        else:
            total = len(flashcards)
            idx = st.session_state.fc_index
            card = flashcards[idx]

            # Progress
            st.progress((idx + 1) / total)
            st.markdown(f'<div class="fc-counter">Card {idx + 1} of {total}</div>', unsafe_allow_html=True)

            # Card front
            st.markdown(f'<div class="fc-front">💡 {card.get("front", card.get("question", ""))}</div>', unsafe_allow_html=True)

            # Reveal/hide back
            if st.session_state.fc_reveal:
                st.markdown(f'<div class="fc-back">📖 {card.get("back", card.get("answer", ""))}</div>', unsafe_allow_html=True)

            # Controls
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                if st.button("◀ Prev", key="fc_prev", use_container_width=True):
                    st.session_state.fc_index = max(0, idx - 1)
                    st.session_state.fc_reveal = False
                    st.rerun()
            with c2:
                reveal_label = "🙈 Hide" if st.session_state.fc_reveal else "👁 Reveal"
                if st.button(reveal_label, key="fc_reveal_btn", use_container_width=True, type="primary"):
                    st.session_state.fc_reveal = not st.session_state.fc_reveal
                    st.rerun()
            with c3:
                if st.button("Next ▶", key="fc_next", use_container_width=True):
                    st.session_state.fc_index = min(total - 1, idx + 1)
                    st.session_state.fc_reveal = False
                    st.rerun()
            with c4:
                if st.button("🔄 Reset", key="fc_reset", use_container_width=True):
                    st.session_state.flashcards = []
                    st.session_state.fc_index = 0
                    st.session_state.fc_reveal = False
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# ── EXAM PREP PANEL ──
# ═══════════════════════════════════════════════════════════════════
elif tool == "exam":
    st.markdown('<div class="panel-wrap">', unsafe_allow_html=True)
    st.markdown("""
    <div class="panel-title">
        🎯 <span>Exam Preparation</span>
    </div>
    """, unsafe_allow_html=True)

    if not has_docs:
        st.info("📄 Upload a PDF document to generate exam preparation materials.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            if len(docs) > 1:
                doc_opts = {v["name"]: k for k, v in docs.items()}
                chosen = st.selectbox("Document", list(doc_opts.keys()), key="exam_doc")
                ex_doc_id = doc_opts[chosen]
            else:
                ex_doc_id = list(docs.keys())[0]
                st.markdown(f'<div class="panel-section-label">{list(docs.values())[0]["name"]}</div>', unsafe_allow_html=True)

        with col2:
            prep_type = st.radio("Type", ["key_points", "practice_questions", "study_guide"],
                                 key="exam_type", horizontal=False)
        with col3:
            ex_diff = st.radio("Level", ["beginner", "intermediate", "advanced"],
                               key="exam_diff", horizontal=False, index=1)

        cache_key = f"{ex_doc_id}_{prep_type}_{ex_diff}"

        if st.button("🎯 Generate Exam Prep", type="primary", key="gen_exam"):
            with st.spinner("🎯 Preparing exam materials…"):
                ok, content, _ = get_exam(ex_doc_id, prep_type, ex_diff)
            if ok:
                st.session_state.exam_cache[cache_key] = content
            else:
                st.error(f"❌ Error: {content}")

        if cache_key in st.session_state.exam_cache:
            content = st.session_state.exam_cache[cache_key]
            st.markdown(f'<div class="content-block">{content}</div>', unsafe_allow_html=True)
            st.download_button(
                "⬇️ Download Exam Prep",
                data=content,
                file_name=f"exam_prep_{prep_type}.txt",
                mime="text/plain",
                key="dl_exam"
            )

    st.markdown('</div>', unsafe_allow_html=True)