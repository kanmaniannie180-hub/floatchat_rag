
import chromadb
import google.generativeai as genai

# -----------------------
# Gemini API Key
# -----------------------
genai.configure(api_key="AIzaSyDIMDdbVm0h4nMEL-nUwzgnPb1UdFKgNNU")

model = genai.GenerativeModel("gemini-2.5-flash")

# -----------------------
# ChromaDB
# -----------------------
client = chromadb.PersistentClient(
    path="rag/chroma_db"
)

collection = client.get_collection(
    name="argo_profiles"
)


def ask_floatchat(query: str):
    """
    RAG Pipeline

    Question
        ↓
    ChromaDB Retrieval
        ↓
    Retrieved Profiles
        ↓
    Gemini
        ↓
    Scientific Explanation
    """

    results = collection.query(
        query_texts=[query],
        n_results=3
    )

    # -----------------------
    # Retrieved Data
    # -----------------------
    retrieved_ids = results["ids"][0]
    retrieved_docs = results["documents"][0]

    # NEW
    retrieved_distances = results["distances"][0]

    context = "\n\n".join(retrieved_docs)

    prompt = f"""
    You are an oceanographic scientific assistant.

    Use ONLY the information provided below.

    Context:
    {context}

    Question:
    {query}

    Provide a scientific explanation.
    """

    response = model.generate_content(prompt)

    return {
        "answer": response.text,
        "sources": retrieved_ids,
        "documents": retrieved_docs,
        "distances": retrieved_distances
    }


# -----------------------
# Terminal Testing
# -----------------------
if __name__ == "__main__":

    query = input("Ask a question: ")

    result = ask_floatchat(query)

    print("\n" + "=" * 80)
    print("RETRIEVED PROFILES")
    print("=" * 80)

    for source in result["sources"]:
        print(source)

    print("\n" + "=" * 80)
    print("ANSWER")
    print("=" * 80)

    print(result["answer"])

