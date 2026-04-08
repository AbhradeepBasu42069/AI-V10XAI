import os
import json
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import Json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from auth import validate_api_key
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter(prefix="/vector-storage",
    tags=["Vector Storage Operations"],
    dependencies=[Depends(validate_api_key)])

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'resume_search'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': os.getenv('DB_PORT', '5432')
}

class VectorStorageRequest(BaseModel):
    profile_id: int
    embedding: List[float]
    metadata: Dict[str, Any] = None  # Additional data like name, skills, etc.

def get_db_connection():
    """Establish database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

def create_table_if_not_exists():
    """Create the vector_embeddings table if it doesn't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS vector_embeddings (
        profile_id INTEGER PRIMARY KEY,
        embedding JSONB,
        metadata JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    try:
        cursor.execute(create_table_query)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Table creation failed: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.post("/store")
def store_vector_embedding(request: VectorStorageRequest):
    """Store vector embedding in PostgreSQL"""
    try:
        # Ensure table exists
        create_table_if_not_exists()

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert or update the vector
        upsert_query = """
        INSERT INTO vector_embeddings (profile_id, embedding, metadata)
        VALUES (%s, %s, %s)
        ON CONFLICT (profile_id)
        DO UPDATE SET
            embedding = EXCLUDED.embedding,
            metadata = EXCLUDED.metadata,
            updated_at = CURRENT_TIMESTAMP;
        """

        cursor.execute(upsert_query, (
            request.profile_id,
            Json(request.embedding),
            Json(request.metadata) if request.metadata else None
        ))

        conn.commit()
        return {"profile_id": request.profile_id, "status": "stored successfully"}

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Storage failed: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@router.get("/health")
def storage_health_check():
    """Check database connectivity"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        cursor.close()
        conn.close()
        return {"status": "database connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database health check failed: {str(e)}")