"""
AI Notes Summarizer - Streamlit Frontend
==========================================
A modern, clean UI that lets users paste notes or upload TXT/PDF files
and sends them to the FastAPI backend for AI-powered summarisation.
"""

import streamlit as st
import requests
from PyPDF2 import PdfReader
import io

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Notes Summarizer",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Backend URL
# ---------------------------------------------------------------------------
BACKEND_URL = "http://localhost:8000"

# ---------------------------------------------------------------------------
# Custom CSS for a modern, polished look
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* ---- Import Google Font ---- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ---- Global ---- */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ---- Main header ---- */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.25);
    }
    .main-header h1 {
        color: #ffffff;
        font-size: 2.6rem;
        font-weight: 800;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: rgba(255, 255, 255, 0.88);
        font-size: 1.1rem;
        margin: 0;
        font-weight: 400;
    }

    /* ---- Summary card ---- */
    .summary-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 14px;
        margin: 1.2rem 0;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    .summary-card h3 {
        color: #2d3748;
        margin-top: 0;
    }
    .summary-card p {
        color: #4a5568;
        line-height: 1.75;
        font-size: 1.02rem;
    }

    /* ---- Metric cards ---- */
    .metric-card {
        background: #ffffff;
        padding: 1.4rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    .metric-label {
        font-size: 0.88rem;
        color: #718096;
        margin-top: 0.25rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* ---- Sidebar styling ---- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #e2e8f0 !important;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li,
    section[data-testid="stSidebar"] .stMarkdown span {
        color: #cbd5e0 !important;
    }

    /* ---- Status badge ---- */
    .status-badge {
        display: inline-block;
        padding: 0.35rem 1rem;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    .status-online  { background: #c6f6d5; color: #22543d; }
    .status-offline { background: #fed7d7; color: #742a2a; }

    /* ---- Button override ---- */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2.5rem;
        font-size: 1.05rem;
        font-weight: 600;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.45);
    }

    /* ---- Divider ---- */
    .fancy-divider {
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2, #667eea);
        border: none;
        border-radius: 2px;
        margin: 1.5rem 0;
    }

    /* ---- Footer ---- */
    .footer {
        text-align: center;
        padding: 1.5rem 0 0.5rem;
        color: #a0aec0;
        font-size: 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def extract_text_from_pdf(uploaded_file) -> str:
    """Read all pages from an uploaded PDF and return the concatenated text."""
    try:
        reader = PdfReader(io.BytesIO(uploaded_file.read()))
        pages_text = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages_text)
    except Exception as exc:
        st.error(f"Failed to read PDF: {exc}")
        return ""


def extract_text_from_txt(uploaded_file) -> str:
    """Decode a plain-text upload and return its content."""
    try:
        return uploaded_file.read().decode("utf-8")
    except Exception as exc:
        st.error(f"Failed to read TXT file: {exc}")
        return ""


def check_backend_health() -> bool:
    """Return True if the FastAPI backend is reachable."""
    try:
        resp = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return resp.status_code == 200
    except requests.ConnectionError:
        return False


def call_summarize_api(text: str) -> dict | None:
    """Send text to the backend /summarize endpoint and return the JSON."""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/summarize",
            json={"text": text},
            timeout=120,  # Summarisation of large texts can be slow
        )
        if resp.status_code == 200:
            return resp.json()
        else:
            error_detail = resp.json().get("detail", "Unknown error")
            st.error(f"API Error: {error_detail}")
            return None
    except requests.ConnectionError:
        st.error("⚠️ Cannot reach the backend. Make sure FastAPI is running on port 8000.")
        return None
    except requests.Timeout:
        st.error("⚠️ The request timed out. The text may be too long – try a shorter input.")
        return None


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## 📝 AI Notes Summarizer")
    st.markdown("---")

    # Backend status
    is_online = check_backend_health()
    if is_online:
        st.markdown(
            '<span class="status-badge status-online">● Backend Online</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="status-badge status-offline">● Backend Offline</span>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    st.markdown("### ℹ️ About")
    st.markdown(
        "This app uses state-of-the-art NLP to condense long notes "
        "into concise, readable summaries — saving you time and effort."
    )

    st.markdown("---")

    st.markdown("### 🛠️ Tech Stack")
    st.markdown(
        """
        - **Frontend:** Streamlit
        - **Backend:** FastAPI
        - **AI / NLP:** HuggingFace Transformers
        - **Model:** `distilbart-cnn-12-6`
        - **PDF parsing:** PyPDF2
        """
    )

    st.markdown("---")

    st.markdown("### 🤖 Model Details")
    st.markdown(
        """
        **sshleifer/distilbart-cnn-12-6**

        A distilled version of BART fine-tuned on the CNN / DailyMail
        summarisation dataset. It provides a strong balance of quality
        and speed for abstractive summarisation tasks.
        """
    )

    st.markdown("---")
    st.markdown(
        '<p style="text-align:center;color:#718096;font-size:0.78rem;">'
        "Made with ❤️ using Streamlit + FastAPI</p>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------

# Header
st.markdown(
    """
    <div class="main-header">
        <h1>📝 AI Notes Summarizer</h1>
        <p>Paste your notes or upload a file — get an instant, AI-powered summary with key analytics.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Two-column input area
# ---------------------------------------------------------------------------
col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown("### ✍️ Paste Your Notes")
    user_text = st.text_area(
        label="Enter your notes here",
        height=280,
        placeholder="Paste your lecture notes, meeting minutes, articles, or any long text here …",
        label_visibility="collapsed",
    )

with col_right:
    st.markdown("### 📂 Or Upload a File")
    uploaded_file = st.file_uploader(
        "Upload a TXT or PDF file",
        type=["txt", "pdf"],
        label_visibility="collapsed",
    )

    if uploaded_file:
        st.success(f"📄 **{uploaded_file.name}** uploaded ({uploaded_file.size:,} bytes)")

# ---------------------------------------------------------------------------
# Determine the final text to summarise
# ---------------------------------------------------------------------------
final_text = ""

if uploaded_file:
    if uploaded_file.name.lower().endswith(".pdf"):
        final_text = extract_text_from_pdf(uploaded_file)
    else:
        final_text = extract_text_from_txt(uploaded_file)

    if final_text:
        with st.expander("📖 Extracted text preview", expanded=False):
            st.text(final_text[:2000] + (" …" if len(final_text) > 2000 else ""))
elif user_text:
    final_text = user_text

# ---------------------------------------------------------------------------
# Summarise button
# ---------------------------------------------------------------------------
st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)

_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    summarize_clicked = st.button("🚀  Summarize Notes", use_container_width=True)

# ---------------------------------------------------------------------------
# Run summarisation
# ---------------------------------------------------------------------------
if summarize_clicked:
    if not final_text.strip():
        st.warning("⚠️ Please enter some text or upload a file before summarising.")
    elif not is_online:
        st.error(
            "⚠️ The backend is not reachable. Start the FastAPI server first:\n\n"
            "```\ncd backend\nuvicorn app:app --reload\n```"
        )
    else:
        with st.spinner("🧠 Generating summary — this may take a moment …"):
            result = call_summarize_api(final_text)

        if result:
            st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)

            # --- Metrics row ---
            st.markdown("### 📊 Summary Analytics")
            m1, m2, m3, m4 = st.columns(4)

            with m1:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-value">{result["original_word_count"]:,}</div>
                        <div class="metric-label">Original Words</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with m2:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-value">{result["summary_word_count"]:,}</div>
                        <div class="metric-label">Summary Words</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with m3:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-value">{result["compression_percentage"]}%</div>
                        <div class="metric-label">Compression</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with m4:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-value">{result["processing_time"]}s</div>
                        <div class="metric-label">Processing Time</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("")

            # --- Summary card ---
            st.markdown("### 📋 Generated Summary")
            st.markdown(
                f"""
                <div class="summary-card">
                    <p>{result["summary"]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # --- Download button ---
            st.download_button(
                label="⬇️  Download Summary as TXT",
                data=result["summary"],
                file_name="summary.txt",
                mime="text/plain",
            )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="footer">
        AI Notes Summarizer &copy; 2026 &nbsp;|&nbsp; Built with Streamlit &amp; FastAPI
    </div>
    """,
    unsafe_allow_html=True,
)
