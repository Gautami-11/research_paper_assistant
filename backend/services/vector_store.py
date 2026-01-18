import os
import uuid
from pinecone import Pinecone
from services.embeddings import embed_text
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
INDEX_NAME = "research-paper-rag"
index = pc.Index(INDEX_NAME)

def add_records(records: list[dict], namespace: str):
    texts = [r["text"] for r in records]
    embeddings = embed_text(texts)
    
    vectors = []
    for i, record in enumerate(records):
        vector_id = str(uuid.uuid4())
        citation_str = ",".join(record["citations"]) if isinstance(record["citations"], list) else str(record["citations"])
        
        metadata = {
            "text": record["text"],
            "section": record["section"],
            "citations": citation_str
        }
        
        vectors.append({
            "id": vector_id,
            "values": embeddings[i],
            "metadata": metadata
        })

    # ✅ FIX: Upload in batches of 100 to avoid "Message too large" error
    BATCH_SIZE = 100
    total_vectors = len(vectors)
    
    print(f"📦 Starting upload of {total_vectors} vectors to Namespace: {namespace}...")

    for i in range(0, total_vectors, BATCH_SIZE):
        batch = vectors[i : i + BATCH_SIZE]
        index.upsert(vectors=batch, namespace=namespace)
        print(f"   - Uploaded batch {i} to {i + len(batch)}")

    print("✅ Upload complete!")

def query_records(query: str, namespace: str, top_k: int = 5):
    query_embedding = embed_text([query])[0]

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        namespace=namespace 
    )

    if not results["matches"]:
        return []

    output = []
    for match in results["matches"]:
        meta = match["metadata"]
        raw_citations = meta.get("citations", "")
        
        output.append({
            "text": meta.get("text", ""),
            "section": meta.get("section", "Unknown"),
            "citations": raw_citations.split(",") if raw_citations else []
        })

    return output