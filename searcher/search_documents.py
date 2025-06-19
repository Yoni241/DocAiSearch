import os
import psycopg2
import numpy as np
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Configure Gemini
genai.configure(api_key=api_key)

# Get user query
query = input("🔍 Enter your search query: ")

# Generate embedding using Gemini embedding model
embedding_model = genai.embed_content(
    model="models/embedding-001",
    content=query,
    task_type="retrieval_query"
)
query_embedding = np.array(embedding_model["embedding"], dtype=np.float32)

print(f"✅ Got embedding with length {len(query_embedding)}")

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)
cursor = conn.cursor()

# Perform score search using cosine similarity in SQL
cursor.execute("""
    SELECT 
        chunk_text, 
        1 - (embedding <=> %s::vector) AS score,
        filename,
        created_at
    FROM document_chunks
    ORDER BY score DESC
    LIMIT 5;
""", (query_embedding.tolist(),))

results = cursor.fetchall()

print("\n🔎 Top 5 matching chunks:\n")
for i, (chunk_text, score, filename, created_at) in enumerate(results, 1):
    print(f"{i}. 📄 File: {filename} | 🕒 Added: {created_at}")
    print(f"   🔗 Score: {score:.4f}")
    print(f"   📝 Chunk: {chunk_text[:200]}...\n")

cursor.close()
conn.close()
