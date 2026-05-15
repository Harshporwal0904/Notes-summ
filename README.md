# 📝 AI Notes Summarizer

A full-stack AI-powered Notes Summarizer that condenses long text into concise summaries using state-of-the-art NLP. Paste notes or upload TXT/PDF files and get instant summaries with key analytics.

---

## ✨ Features

| Feature | Description |
|---|---|
| **Text Input** | Paste any long-form text directly into the app |
| **File Upload** | Upload `.txt` or `.pdf` files for summarisation |
| **AI Summarisation** | Uses HuggingFace `distilbart-cnn-12-6` for high-quality abstractive summaries |
| **Smart Chunking** | Automatically splits large texts into digestible chunks |
| **Analytics Dashboard** | Original word count, summary word count, compression %, and processing time |
| **Download** | Export your summary as a `.txt` file |
| **Health Check** | Built-in backend status indicator in the sidebar |

---

## 🛠️ Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/)
- **Backend:** [FastAPI](https://fastapi.tiangolo.com/)
- **AI / NLP:** [HuggingFace Transformers](https://huggingface.co/docs/transformers/)
- **Model:** [`sshleifer/distilbart-cnn-12-6`](https://huggingface.co/sshleifer/distilbart-cnn-12-6)
- **PDF Parsing:** PyPDF2
- **HTTP:** Requests

---

## 📁 Project Structure

```
ai-notes-summarizer/
│
├── backend/
│   ├── app.py              # FastAPI server & summarisation logic
│   └── requirements.txt    # Backend dependencies
│
├── frontend/
│   ├── app.py              # Streamlit UI
│   └── requirements.txt    # Frontend dependencies
│
└── README.md               # You are here
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+**
- **pip** (Python package manager)

### 1. Clone the Repository

```bash
git clone <repo-url>
cd ai-notes-summarizer
```

### 2. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

> **Note:** The first run will download the `distilbart-cnn-12-6` model (~1.2 GB). Make sure you have a stable internet connection.

### 3. Install Frontend Dependencies

```bash
cd ../frontend
pip install -r requirements.txt
```

---

## ▶️ Running the Application

You need **two terminals** — one for the backend and one for the frontend.

### Terminal 1 — Start the Backend (FastAPI)

```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at **http://localhost:8000**.  
Swagger docs: **http://localhost:8000/docs**

### Terminal 2 — Start the Frontend (Streamlit)

```bash
cd frontend
streamlit run app.py
```

The UI will open in your browser at **http://localhost:8501**.

---

## 📡 API Endpoints

### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "model": "sshleifer/distilbart-cnn-12-6",
  "message": "AI Notes Summarizer API is running."
}
```

### `POST /summarize`

Summarise a block of text.

**Request body:**
```json
{
  "text": "Your long text here..."
}
```

**Response:**
```json
{
  "summary": "Condensed summary text...",
  "original_word_count": 500,
  "summary_word_count": 85,
  "compression_percentage": 83.0,
  "processing_time": 2.45
}
```

---

## 📸 Screenshots

> _Add screenshots of the application here._

| View | Screenshot |
|---|---|
| **Main Interface** | _screenshot placeholder_ |
| **Summary Result** | _screenshot placeholder_ |
| **PDF Upload** | _screenshot placeholder_ |

---

## 🧠 How It Works

1. **Input** — The user pastes text or uploads a TXT/PDF file via the Streamlit frontend.
2. **Extraction** — For PDF uploads, text is extracted page-by-page using PyPDF2.
3. **Chunking** — Long text is split into ~800-character segments at sentence boundaries.
4. **Summarisation** — Each chunk is summarised independently by `distilbart-cnn-12-6`.
5. **Aggregation** — Per-chunk summaries are concatenated into a single final summary.
6. **Analytics** — Word counts and compression ratio are calculated and returned.

---

## ⚠️ Troubleshooting

| Issue | Solution |
|---|---|
| `Backend Offline` badge in sidebar | Make sure the FastAPI server is running on port 8000 |
| Slow first request | The model is loading into memory — subsequent requests will be faster |
| `torch` installation issues | Visit [pytorch.org](https://pytorch.org/get-started/locally/) for platform-specific instructions |
| PDF text extraction is empty | The PDF may contain scanned images — only text-based PDFs are supported |

---

## 📄 Licence

This project is open-source and available under the [MIT Licence](https://opensource.org/licenses/MIT).

---

> Built with ❤️ using **Streamlit** + **FastAPI** + **HuggingFace Transformers**
