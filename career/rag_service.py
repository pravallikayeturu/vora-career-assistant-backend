from pathlib import Path
from functools import lru_cache

import chromadb
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

from django.conf import settings


# ==========================================
# CONFIGURATION
# ==========================================

CHROMA_DB_PATH = Path(settings.BASE_DIR) / "chroma_db"

COLLECTION_NAME = "vora_resume_chunks"

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_SIZE = 700
CHUNK_OVERLAP = 100
DEFAULT_TOP_K = 4


# ==========================================
# CHROMADB CLIENT
# ==========================================

chroma_client = chromadb.PersistentClient(
    path=str(CHROMA_DB_PATH)
)

resume_collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"},
)


# ==========================================
# LOAD EMBEDDING MODEL ONLY WHEN NEEDED
# ==========================================

@lru_cache(maxsize=1)
def get_embedding_model():
    """
    Load the local embedding model once and reuse it.
    The first load may download the model from Hugging Face.
    """

    return SentenceTransformer(EMBEDDING_MODEL_NAME)


# ==========================================
# TEXT SPLITTER
# ==========================================

def split_resume_text(resume_text):
    """
    Split resume text into overlapping chunks.
    """

    if not isinstance(resume_text, str) or not resume_text.strip():
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    return [
        chunk.strip()
        for chunk in splitter.split_text(resume_text)
        if chunk.strip()
    ]


# ==========================================
# CREATE EMBEDDINGS
# ==========================================

def create_embeddings(texts):
    """
    Convert text chunks into vectors using a local model.
    This does not call the Gemini API.
    """

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    return embeddings.tolist()


# ==========================================
# INDEX A USER'S RESUME
# ==========================================

def index_resume(resume_text, user_id, resume_id):
    """
    Split and store one resume in ChromaDB.

    Each chunk is tagged with its user_id and resume_id
    so retrieval can be restricted to that resume.
    """

    if not isinstance(resume_text, str) or not resume_text.strip():
        return 0

    chunks = split_resume_text(resume_text)

    if not chunks:
        return 0

    # Use deterministic IDs so re-indexing replaces old chunks.
    chunk_ids = [
        f"user_{user_id}_resume_{resume_id}_chunk_{index}"
        for index in range(len(chunks))
    ]

    # Remove previously indexed chunks for this resume.
    # ChromaDB's where filter also limits this to the owner.
    resume_collection.delete(
        where={
            "$and": [
                {"user_id": int(user_id)},
                {"resume_id": int(resume_id)},
            ]
        }
    )

    embeddings = create_embeddings(chunks)

    metadatas = [
        {
            "user_id": int(user_id),
            "resume_id": int(resume_id),
            "chunk_index": index,
        }
        for index in range(len(chunks))
    ]

    # ChromaDB add() stores chunks, vectors, and metadata.
    resume_collection.add(
        ids=chunk_ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return len(chunks)


# ==========================================
# RETRIEVE RELEVANT RESUME CHUNKS
# ==========================================

def retrieve_relevant_chunks(
    question,
    user_id,
    resume_id,
    top_k=DEFAULT_TOP_K,
):
    """
    Retrieve relevant chunks from the specified user's
    specified resume only.
    """

    if not isinstance(question, str) or not question.strip():
        return []

    if not user_id or not resume_id:
        return []

    # Restrict the search to the correct user and resume.
    existing_count = resume_collection.count(
        where={
            "$and": [
                {"user_id": int(user_id)},
                {"resume_id": int(resume_id)},
            ]
        }
    )

    if existing_count == 0:
        return []

    query_embedding = create_embeddings([question])[0]

    results = resume_collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, existing_count),
        where={
            "$and": [
                {"user_id": int(user_id)},
                {"resume_id": int(resume_id)},
            ]
        },
        include=["documents", "metadatas", "distances"],
    )

    documents = results.get("documents") or []

    if not documents or not documents[0]:
        return []

    return documents[0]


# ==========================================
# BUILD RETRIEVED CONTEXT
# ==========================================

def get_resume_context(question, resume_text, user_id, resume_id):
    """
    Ensure the resume is indexed and return relevant chunks.

    If retrieval fails, the caller can fall back to the
    existing full-text resume context.
    """

    if not resume_text or not resume_text.strip():
        return ""

    # Index the resume if this is the first request.
    count = resume_collection.count(
    where={
        "$and": [
            {"user_id": int(user_id)},
            {"resume_id": int(resume_id)},
        ]
    }
)

    if count == 0:
        index_resume(
            resume_text=resume_text,
            user_id=user_id,
            resume_id=resume_id,
        )

    chunks = retrieve_relevant_chunks(
        question=question,
        user_id=user_id,
        resume_id=resume_id,
    )

    return "\n\n".join(chunks)
