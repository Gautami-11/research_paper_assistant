from fastapi import FastAPI, UploadFile, File, Form, Header
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
from services.rag import store_paper, retrieve_chunks
from llm import generate_answer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...), 
    session_id: str = Form(...)  # ✅ Receives ID from Frontend Form
):
    reader = PdfReader(file.file)
    text = "".join(page.extract_text() or "" for page in reader.pages)

    # Store in this user's specific folder
    store_paper(text, session_id)

    return {"status": "PDF indexed", "session_id": session_id}

@app.post("/ask")
def ask_question(
    query: str, 
    session_id: str = Header(None) # ✅ Receives ID from Headers
):
    if not session_id:
        return {"answer": "Session ID missing."}

    # Search only in this user's folder
    chunks = retrieve_chunks(query, session_id)

    if not chunks:
        return {"answer": "I could not find relevant information in your specific paper."}

    context = ""
    for c in chunks:
        citation = ",".join(c["citations"]) if c.get("citations") else ""
        context += f"{c['text']} {f'[{citation}]' if citation else ''}\n"

    answer = generate_answer(query, context)
    return {"answer": answer}