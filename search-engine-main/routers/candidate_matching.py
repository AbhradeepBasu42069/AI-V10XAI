import os
import json
from typing import List, Dict, Any, Optional
import numpy as np
from google import genai
from google.genai import types
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from auth import validate_api_key
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter(prefix="/candidate-matching",
    tags=["Candidate Matching Operations"],
    dependencies=[Depends(validate_api_key)])

# Database configuration (same as vector_storage.py)
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'resume_search'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': os.getenv('DB_PORT', '5432')
}

# Initialize Gemini client for job embedding
genai_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

class JobMatchingRequest(BaseModel):
    job_description: Optional[str] = None  # Job text to embed
    job_vector: Optional[List[float]] = None  # Pre-computed job vector
    top_k: int = 10  # Number of top matches to return

class MatchResult(BaseModel):
    profile_id: int
    similarity_score: float
    match_percentage: float
    metadata: Dict[str, Any]

def get_db_connection():
    """Establish database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

def generate_job_embedding(job_description: str) -> List[float]:
    """Generate embedding for job description using Gemini"""
    try:
        response = genai_client.models.embed_content(
            model="gemini-embedding-001",
            contents=job_description,
            config={'output_dimensionality': 768}
        )
        return response.embeddings[0].values
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job embedding generation failed: {str(e)}")

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    return dot_product / (norm_v1 * norm_v2) if norm_v1 != 0 and norm_v2 != 0 else 0.0

def get_all_candidate_vectors() -> List[Dict[str, Any]]:
    """Retrieve all candidate vectors and metadata from database"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        query = "SELECT profile_id, embedding, metadata FROM vector_embeddings;"
        cursor.execute(query)
        results = cursor.fetchall()

        candidates = []
        for row in results:
            # embedding is stored as JSON array
            embedding = row['embedding']

            candidates.append({
                'profile_id': row['profile_id'],
                'embedding': embedding,
                'metadata': row['metadata'] or {}
            })

        return candidates

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve candidates: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.post("/match", response_model=List[MatchResult])
def match_candidates(request: JobMatchingRequest):
    """Find best matching candidates for a job posting"""
    try:
        # Get job vector
        if request.job_vector:
            job_vector = request.job_vector
        elif request.job_description:
            job_vector = generate_job_embedding(request.job_description)
        else:
            raise HTTPException(status_code=400, detail="Either job_description or job_vector must be provided")

        # Retrieve all candidate vectors
        candidates = get_all_candidate_vectors()

        if not candidates:
            return []

        # Calculate similarities
        matches = []
        for candidate in candidates:
            similarity = cosine_similarity(job_vector, candidate['embedding'])
            match_percentage = round(similarity * 100, 2)  # Convert to percentage

            matches.append(MatchResult(
                profile_id=candidate['profile_id'],
                similarity_score=round(similarity, 4),
                match_percentage=match_percentage,
                metadata=candidate['metadata']
            ))

        # Sort by similarity score in descending order
        matches.sort(key=lambda x: x.similarity_score, reverse=True)

        # Return top k matches
        return matches[:request.top_k]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Matching failed: {str(e)}")

@router.get("/health")
def matching_health_check():
    """Check matching service health"""
    try:
        # Check database connectivity
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM vector_embeddings;")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        return {
            "status": "healthy",
            "total_candidates": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")