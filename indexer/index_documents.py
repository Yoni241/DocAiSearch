import os
from docx import Document
import fitz  # PyMuPDF
import re 
from dotenv import load_dotenv
import google.generativeai as genai
import psycopg2

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def extract_text_from_docx(filepath):
    doc = Document(filepath)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    
def extract_text_from_pdf(filepath):
    text = ""
    with fitz.open(filepath) as doc:
        for page in doc:
            text += page.get_text()
        return text
        
def extract_text(filepath):
    if filepath.endswith(".docx"):
        return extract_text_from_docx(filepath)
    elif filepath.endswith(".pdf"):
        return extract_text_from_pdf(filepath)
    else:
        raise ValueError("Unsupported file format. Please provide a .docx/.pdf file only")

def split_text_fixed(text, chunk_size=300, overlap=50):
    """
    Splits a long string into fixed-size chunks with overlap, for use in RAG pipelines.

    This method helps handle long texts that exceed token limits of LLMs by dividing
    them into equal-length segments. Overlap between chunks ensures that important 
    context is preserved when a sentence spans across two chunks.

    Args:
        text (str): The full input text to split.
        chunk_size (int): Maximum number of characters per chunk.
        overlap (int): Number of overlapping characters between consecutive chunks.

    Returns:
        list of str: List of overlapping text chunks.
    """
    
    chunks = []
    start = 0;
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks
    
def split_text_sentences(text, num_sentences=3):
    """
    Splits text into chunks based on a fixed number of sentences.

    This method uses punctuation (.!? followed by whitespace) to segment the input 
    into sentences, then groups every N sentences into a chunk. This approach helps 
    preserve semantic meaning better than fixed-size chunking.

    Args:
        text (str): The full input text to split.
        num_sentences (int): Number of sentences per chunk.

    Returns:
        list of str: List of sentence-based chunks.
    """

    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    for i in range(0, len(sentences), num_sentences):
        chunk = " ".join(sentences[i:i+num_sentences])
        if chunk:
            chunks.append(chunk)
    return chunks
    
def split_text_paragraphs(text):
    """
    Splits text into chunks based on paragraphs.

    This method detects paragraphs separated by double newlines ("\n\n").
    It works well for structured documents like reports, catalogs, and manuals,
    where logical content is already divided into paragraphs.

    Args:
        text (str): The full input text to split.

    Returns:
        list of str: List of paragraph-based chunks.
    """
    paragraphs = text.split("\n\n")
    return [p.strip() for p in paragraphs if p.strip()]
    
def split_text(text, method="fixed", **kwargs):
    if method == "fixed":
        return split_text_fixed(text, **kwargs)
    elif method == "sentences":
        return split_text_sentences(text, **kwargs)
    elif method == "paragraphs":
        return split_text_paragraphs(text)
    else:
        raise ValueError("Invalid method. Use: fixed / sentences / paragraphs")

def generate_embedding(chunk):
    model = genai.embed_content(
        model="models/embedding-001",
        content=chunk,
        task_type="retrieval_document"
    )
    return model["embedding"]

def store_chunks_in_db(chunks, embeddings):
    connection = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = connection.cursor()

    # Create table IF NOT EXIST
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    chunk_text TEXT,
    embedding VECTOR(768),
    filename TEXT,
    split_strategy TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
    """)

    for chunk, embedding in zip(chunks, embeddings):
        cursor.execute(
            """
        INSERT INTO document_chunks (chunk_text, embedding, filename, split_strategy)
        VALUES (%s, %s, %s, %s)
        """,
        (chunk, embedding, "../data/ksp_example_catalog.pdf", "fixed")
        )

    connection.commit()
    cursor.close()
    connection.close()

# -----------------------------------MAIN------------------------------------------

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(SCRIPT_DIR, "../data/ksp_example_catalog.pdf")
    filepath = os.path.abspath(filepath)
    text = extract_text(filepath)
    print(" ---                       📄 Extracted Text:                      --- ")
    print(text)
    print(" --------------------------------------------------------------------- ")
    
    print("")

    # Create chunks using the fixed method
    chunks_fixed = split_text(text, method="fixed", chunk_size=100, overlap=20)
    print("\n ---                   📚 Fixed-based-Chunks:                      --- ")
    for i, chunk in enumerate(chunks_fixed):
        print(f"\n--- Chunk #{i+1} ---\n{chunk}")
    
    print(" --------------------------------------------------------------------- ")

    # Generate embeddings for each chunk
    embeddings = []
    for i, chunk in enumerate(chunks_fixed):
        embedding = generate_embedding(chunk)
        embeddings.append(embedding)
        print(f"Embedding {i}: Length = {len(embedding)}")

    # Store chunks + embeddings in PostgreSQL
    store_chunks_in_db(chunks_fixed, embeddings)
    print("\n✅ All chunks and embeddings have been stored in the database.\n")

    # Optional: also print sentence and paragraph chunks for comparison
    chunks_sentences = split_text(text, method="sentences")
    print("\n ---                    📚 Sentence-based-Chunks:                 --- ")
    for i, chunk in enumerate(chunks_sentences, 1):
        print(f"Chunk {i}: {chunk}")
    
    print(" --------------------------------------------------------------------- ")
    
    chunks_paragraphs = split_text(text, method="paragraphs")
    print("\n ---                    📚 Paragraph-based-Chunks:                --- ")
    for i, chunk in enumerate(chunks_paragraphs, 1):
        print(f"Chunk {i}: {chunk}")
    print(" --------------------------------------------------------------------- ")


