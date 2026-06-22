import pickle
import chromadb
from sentence_transformers import SentenceTransformer

# Load documents
with open("rag/documents.pkl", "rb") as f:
    documents = pickle.load(f)

with open("rag/ids.pkl", "rb") as f:
    ids = pickle.load(f)

print("Loaded documents:", len(documents))

# Embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

print("Generating embeddings...")

embeddings = model.encode(
    documents,
    show_progress_bar=True
).tolist()

# Persistent ChromaDB
client = chromadb.PersistentClient(
    path="rag/chroma_db"
)

collection = client.get_or_create_collection(
    name="argo_profiles"
)

collection.add(
    documents=documents,
    embeddings=embeddings,
    ids=ids
)

print("Vector database created successfully!")
print("Documents stored:", len(documents))