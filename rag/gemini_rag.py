import os
import chromadb
import plotly.express as px
import google.generativeai as genai


# ==========================================
# GEMINI CONFIGURATION
# ==========================================

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


# ==========================================
# CHROMADB
# ==========================================

client = chromadb.PersistentClient(
    path="rag/chroma_db"
)

collection = client.get_collection(
    name="argo_profiles"
)

# ==========================================
# REGION DETECTOR
# ==========================================
def detect_region(query):

    q = query.lower()

    if "sri lanka" in q or "srilanka" in q:
        return "Near Sri Lanka, Northern Indian Ocean"

    elif "arabian sea" in q:
        return "Arabian Sea"

    elif "bay of bengal" in q or "bengal" in q:
        return "Bay of Bengal"

    elif "maldives" in q:
        return "Near Maldives"

    return None


# ==========================================
# FLOATCHAT RAG
# ==========================================

def ask_floatchat(query: str):

    """
    Question
        ↓
    ChromaDB Retrieval
        ↓
    Retrieved Profiles
        ↓
    Gemini Scientific Reasoning
        ↓
    Explainable Ocean Intelligence
    """

    # --------------------------------------
    # Retrieve Context
    # --------------------------------------

    # ==========================================
    # METADATA FILTERING
    # ==========================================

    region_filter = detect_region(query)

    if region_filter:

        print(
            f"Applying region filter: {region_filter}"
        )

        results = collection.query(
            query_texts=[query],
            n_results=5,
            where={
                "region": region_filter
            }
        )

    else:

        results = collection.query(
            query_texts=[query],
            n_results=5
        )

    retrieved_ids = results["ids"][0]
    retrieved_docs = results["documents"][0]
    retrieved_distances = results["distances"][0]
    retrieved_metadata = results["metadatas"][0]

    context = "\n\n".join(
        retrieved_docs
    )
    # --------------------------------------
    # Top Retrieved Profile
    # --------------------------------------

    top_profile = retrieved_ids[0]

    
    float_id, cycle = top_profile.rsplit("_", 1)

    # --------------------------------------
    # Prompt
    # --------------------------------------

    prompt = f"""
You are an oceanographic scientific assistant.

Retrieved Profiles (Evidence):
{chr(10).join(f"- Float {pid}" for pid in retrieved_ids)}

Context:
{context}

Question:
{query}

Instructions:

1. Begin the answer with an "Evidence Used" section.
2. List every retrieved profile ID under "Evidence Used".
3. Base the answer ONLY on the retrieved evidence.
4. Identify relevant oceanographic features.
5. Explain temperature behaviour.
6. Explain salinity behaviour.
7. Explain depth-related characteristics.
8. Discuss temporal changes if multiple profile dates are available.
9. Discuss spatial variability using latitude and longitude information.
10. End with a scientific conclusion.
11. Organize the response using the following headings:

- Evidence Used
- Oceanographic Features
- Scientific Analysis
- Conclusion

If the retrieved evidence is insufficient, clearly state that.

Provide a structured scientific explanation.

"""

    # --------------------------------------
    # Gemini Response
    # --------------------------------------

    response = model.generate_content(
        prompt
    )

    # --------------------------------------
    # Return Results
    # --------------------------------------
    top_profile = retrieved_ids[0]

    top_float, top_cycle = top_profile.rsplit("_", 1)
    return {
        "answer": response.text,
        "sources": retrieved_ids,
        "documents": retrieved_docs,
        "distances": retrieved_distances,
        "metadata": retrieved_metadata,
        "top_float": top_float,
        "top_cycle": int(top_cycle),
        "top_profiles": retrieved_ids     
        }


# ==========================================
# TERMINAL TESTING
# ==========================================

if __name__ == "__main__":

    query = input(
        "Ask a question: "
    )

    result = ask_floatchat(
        query
    )

    print("\n" + "=" * 80)
    print("RETRIEVED PROFILES")
    print("=" * 80)

    for source, distance in zip(
        result["sources"],
        result["distances"]
    ):

        print(
            f"{source} | Distance: {round(distance, 4)}"
        )

    print("\n" + "=" * 80)
    print("ANSWER")
    print("=" * 80)

    print(
        result["answer"]
    )
    print("\nTop Float:", result["top_float"])
    print("Top Cycle:", result["top_cycle"])