import re
from typing import List, Dict
from services.vector_store import add_records, query_records

SECTION_PATTERN = re.compile(r"\n[A-Z]\.\s+[A-Za-z ].+\n")

def split_by_sections(text: str) -> List[Dict]:
    matches = list(SECTION_PATTERN.finditer(text))
    if not matches:
        return [{"section": "FULL_TEXT", "text": text}]

    sections = []
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections.append({
            "section": match.group().strip(),
            "text": text[start:end].strip()
        })
    return sections

def extract_sentences(section_text: str) -> List[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", section_text) if len(s.strip()) > 40]

def extract_citations(sentence: str):
    return re.findall(r"\[(\d+)\]", sentence)

def store_paper(text: str, session_id: str):
    sections = split_by_sections(text)
    records = []
    idx = 0

    for sec in sections:
        for sent in extract_sentences(sec["text"]):
            records.append({
                "id": f"sent-{idx}",
                "text": sent,
                "section": sec["section"],
                "citations": extract_citations(sent) or ["none"]
            })
            idx += 1

    if not records:
        raise ValueError("No valid text found")

    add_records(records, namespace=session_id)

def retrieve_chunks(query: str, session_id: str, top_k: int = 8):
    return query_records(query, namespace=session_id, top_k=top_k)