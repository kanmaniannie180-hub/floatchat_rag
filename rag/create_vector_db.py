import pickle
import chromadb
from sentence_transformers import SentenceTransformer

# ==========================================
# LOAD DOCUMENTS
# ==========================================

with open("rag/documents.pkl", "rb") as f:
    documents = pickle.load(f)

with open("rag/ids.pkl", "rb") as f:
    ids = pickle.load(f)

with open("rag/metadatas.pkl", "rb") as f:
    metadatas = pickle.load(f)

print("Loaded documents:", len(documents))

# ==========================================
# EMBEDDING MODEL
# ==========================================

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Generating embeddings...")

embeddings = model.encode(
    documents,
    show_progress_bar=True
).tolist()

# ==========================================
# CHROMADB
# ==========================================

client = chromadb.PersistentClient(
    path="rag/chroma_db"
)

# Delete old collection if exists
try:
    client.delete_collection(
        name="argo_profiles"
    )
    print("Old collection deleted.")
except:
    pass

collection = client.get_or_create_collection(
    name="argo_profiles"
)

# ==========================================
# BATCH INSERT
# ==========================================

batch_size = 100

for i in range(
    0,
    len(documents),
    batch_size
):

    batch_docs = documents[
        i:i + batch_size
    ]

    batch_ids = ids[
        i:i + batch_size
    ]

    batch_embeddings = embeddings[
        i:i + batch_size
    ]

    batch_metadata = metadatas[
        i:i + batch_size
    ]

    collection.add(
        documents=batch_docs,
        embeddings=batch_embeddings,
        ids=batch_ids,
        metadatas=batch_metadata
    )

    print(
        f"Stored {min(i + batch_size, len(documents))} / {len(documents)}"
    )

# ==========================================
# COMPLETE
# ==========================================

print("\nVector database created successfully!")
print("Documents stored:", len(documents))

# ==========================================
# VERIFY METADATA
# ==========================================

sample = collection.get(
    limit=1,
    include=["metadatas"]
)

print("\nSample Metadata:")
print(sample["metadatas"][0])