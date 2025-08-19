from __future__ import annotations

import re
from io import BytesIO
from typing import List, Dict

from fastapi import FastAPI, UploadFile, File, HTTPException
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class KnowledgeBase:
    """In-memory store for document chunks."""

    def __init__(self) -> None:
        self.chunks: List[Dict[str, str]] = []
        self.vectorizer = TfidfVectorizer()
        self.embeddings = None

    def add_document(self, text: str, source: str) -> None:
        """Split text and update embeddings."""
        parts = [p.strip() for p in text.split("\n") if p.strip()]
        for part in parts:
            self.chunks.append({"source": source, "text": part})
        if self.chunks:
            texts = [c["text"] for c in self.chunks]
            self.embeddings = self.vectorizer.fit_transform(texts)

    def query(self, question: str, top_k: int = 1) -> List[Dict[str, str]]:
        if not self.chunks:
            return []
        q_vec = self.vectorizer.transform([question])
        sims = cosine_similarity(q_vec, self.embeddings)[0]
        indices = sims.argsort()[::-1][:top_k]
        return [self.chunks[i] for i in indices]


def mask_sensitive(text: str) -> str:
    """Mask email, phone numbers and IDs."""
    email = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    phone = re.compile(r"\b(?:\+?\d[\d -]{7,}\d)\b")
    taiwan_id = re.compile(r"\b[A-Z][0-9]{9}\b")
    text = email.sub("[EMAIL]", text)
    text = phone.sub("[PHONE]", text)
    text = taiwan_id.sub("[ID]", text)
    return text


app = FastAPI(title="AI Compliance Copilot")
kb = KnowledgeBase()


@app.post("/upload")
async def upload(file: UploadFile = File(...)) -> Dict[str, str]:
    if file.content_type not in {"application/pdf", "text/plain"}:
        raise HTTPException(400, "Unsupported file type")
    data = await file.read()
    if file.content_type == "application/pdf":
        reader = PdfReader(BytesIO(data))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        text = data.decode("utf-8")
    kb.add_document(text, file.filename)
    return {"status": "ok", "chunks": str(len(kb.chunks))}


@app.get("/ask")
async def ask(q: str) -> Dict[str, List[str]]:
    results = kb.query(q, top_k=1)
    if not results:
        return {"answer": "資料不足", "sources": []}
    best = results[0]
    masked = mask_sensitive(best["text"])
    return {"answer": masked, "sources": [best["source"]]}
