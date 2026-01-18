from sentence_transformers import SentenceTransformer

# Load model locally (runs on your CPU)
_model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(texts: list[str]) -> list[list[float]]:
    return _model.encode(texts).tolist()