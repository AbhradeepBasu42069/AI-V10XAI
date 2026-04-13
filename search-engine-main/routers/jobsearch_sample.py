import chromadb
from google import genai
import json

# Initialize Gemini Client
genai_client = genai.Client(api_key="YOUR_API_KEY")

# Initialize ChromaDB (This creates a folder named 'my_vector_db' to save your data)
chroma_client = chromadb.PersistentClient(path="./my_vector_db")
collection = chroma_client.get_or_create_collection(name="candidate_profiles")

def get_768_vector(data):
    """Utility to get embedding from Gemini"""
    res = genai_client.models.embed_content(
        model="text-embedding-004",
        content=json.dumps(data),
        config={'output_dimensionality': 768}
    )
    return res.embeddings[0].values

# 1. ADDING DATA (Run this once per profile)
candidate_data = {"id": "cand_01", "name": "Alice", "skills": "Python, FastAPI"}
vector = get_768_vector(candidate_data)

collection.add(
    embeddings=[vector],
    metadatas=[candidate_data], # Store the original JSON here
    ids=["cand_01"]
)

# 2. SEARCHING (The 'Find Match' step)
query_job = {"role": "Backend Engineer", "reqs": "Python and Cloud"}
query_vector = get_768_vector(query_job)

results = collection.query(
    query_embeddings=[query_vector],
    n_results=3 # Give me the top 3 matches
)

for match in results['metadatas'][0]:
    print(f"Found Match: {match['name']}")