import chromadb

client = chromadb.PersistentClient(
    path="rag/chroma_db"
)

collection = client.get_collection(
    name="argo_profiles"
)

test_queries = [
    "high salinity profile",
    "deep ocean measurements",
    "warm ocean surface"
]

for query in test_queries:

    print("\n" + "=" * 80)
    print("QUERY:", query)
    print("=" * 80)

    results = collection.query(
        query_texts=[query],
        n_results=3
    )

    for i, doc in enumerate(results["documents"][0], start=1):
        print(f"\nResult {i}")
        print("-" * 50)
        print(doc)