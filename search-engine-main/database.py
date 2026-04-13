# ============================================================================
# DATABASE UTILITIES AND SCHEMA MANAGEMENT
# Handles all database operations, connection management, and schema creation
# ============================================================================
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from typing import Optional, Dict, Any, List
from datetime import datetime
from contextlib import contextmanager
from config import DATABASE_CONFIG
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# DATABASE CONNECTION MANAGER
# ============================================================================
class DatabaseManager:
    """Manages database connections and operations"""
    
    @staticmethod
    def get_connection():
        """
        Establish a database connection
        Returns: psycopg2 connection object
        Raises: HTTPException if connection fails
        """
        try:
            conn = psycopg2.connect(
                host=DATABASE_CONFIG['host'],
                database=DATABASE_CONFIG['database'],
                user=DATABASE_CONFIG['user'],
                password=DATABASE_CONFIG['password'],
                port=DATABASE_CONFIG['port']
            )
            return conn
        except psycopg2.Error as e:
            logger.error(f"Database connection failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

    @staticmethod
    @contextmanager
    def get_db_cursor(commit: bool = True):
        """
        Context manager for database operations
        Yields: cursor object
        Automatically handles connection closing and commit/rollback
        """
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
            if commit:
                conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database operation failed: {str(e)}")
            raise
        finally:
            cursor.close()
            conn.close()

# ============================================================================
# DATABASE SCHEMA INITIALIZATION
# ============================================================================
def initialize_database():
    """
    Create all required tables in PostgreSQL
    This should be run once during application startup
    """
    try:
        with DatabaseManager.get_db_cursor(commit=True) as cursor:
            # ================================================================
            # TABLE 1: RECRUITER JOBS
            # ================================================================
            create_recruiter_jobs_table = """
            CREATE TABLE IF NOT EXISTS recruiter_jobs (
                job_id SERIAL PRIMARY KEY,
                recruiter_id VARCHAR(255) NOT NULL,
                job_title VARCHAR(255) NOT NULL,
                job_description TEXT NOT NULL,
                job_embedding JSONB,
                skills_required JSONB,
                experience_required_years FLOAT,
                salary_range_min INTEGER,
                salary_range_max INTEGER,
                location VARCHAR(255),
                employment_type VARCHAR(50),
                industry VARCHAR(100),
                job_category VARCHAR(100),
                required_qualifications TEXT,
                status VARCHAR(50) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT valid_experience CHECK (experience_required_years >= 0)
            );
            """
            cursor.execute(create_recruiter_jobs_table)
            logger.info("Created recruiter_jobs table")
            
            # ================================================================
            # TABLE 2: CANDIDATE PROFILES
            # ================================================================
            create_candidate_profiles_table = """
            CREATE TABLE IF NOT EXISTS candidate_profiles (
                candidate_id SERIAL PRIMARY KEY,
                candidate_name VARCHAR(255) NOT NULL,
                email_address VARCHAR(255) UNIQUE,
                phone_number VARCHAR(20),
                current_location VARCHAR(255),
                parsed_resume_data JSONB,
                profile_embedding JSONB,
                skills JSONB,
                years_of_experience FLOAT,
                current_cgpa FLOAT,
                latest_company VARCHAR(255),
                latest_role_title VARCHAR(255),
                education_degree VARCHAR(100),
                education_institute VARCHAR(255),
                education_branch VARCHAR(100),
                notice_period_days INTEGER,
                work_authorization VARCHAR(100),
                preferred_roles JSONB,
                employment_type_preference VARCHAR(50),
                status VARCHAR(50) DEFAULT 'active',
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT valid_cgpa CHECK (current_cgpa >= 0 AND current_cgpa <= 10),
                CONSTRAINT valid_experience CHECK (years_of_experience >= 0)
            );
            """
            cursor.execute(create_candidate_profiles_table)
            logger.info("Created candidate_profiles table")
            
            # ================================================================
            # TABLE 3: MATCHING RESULTS
            # ================================================================
            create_matching_results_table = """
            CREATE TABLE IF NOT EXISTS matching_results (
                match_id SERIAL PRIMARY KEY,
                job_id INTEGER NOT NULL REFERENCES recruiter_jobs(job_id) ON DELETE CASCADE,
                candidate_id INTEGER NOT NULL REFERENCES candidate_profiles(candidate_id) ON DELETE CASCADE,
                cosine_similarity_score FLOAT NOT NULL,
                match_percentage FLOAT,
                skill_match_score FLOAT,
                experience_match_score FLOAT,
                education_match_score FLOAT,
                location_match_score FLOAT,
                final_weighted_score FLOAT,
                match_details JSONB,
                match_status VARCHAR(50) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT valid_similarity CHECK (cosine_similarity_score >= -1 AND cosine_similarity_score <= 1),
                CONSTRAINT valid_match_percentage CHECK (match_percentage >= 0 AND match_percentage <= 100)
            );
            """
            cursor.execute(create_matching_results_table)
            logger.info("Created matching_results table")
            
            # ================================================================
            # CREATE INDEXES FOR PERFORMANCE
            # ================================================================
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_recruiter_jobs_recruiter_id ON recruiter_jobs(recruiter_id);",
                "CREATE INDEX IF NOT EXISTS idx_recruiter_jobs_status ON recruiter_jobs(status);",
                "CREATE INDEX IF NOT EXISTS idx_candidate_profiles_email ON candidate_profiles(email_address);",
                "CREATE INDEX IF NOT EXISTS idx_candidate_profiles_status ON candidate_profiles(status);",
                "CREATE INDEX IF NOT EXISTS idx_matching_results_job_id ON matching_results(job_id);",
                "CREATE INDEX IF NOT EXISTS idx_matching_results_candidate_id ON matching_results(candidate_id);",
                "CREATE INDEX IF NOT EXISTS idx_matching_results_score ON matching_results(final_weighted_score DESC);",
            ]
            
            for index_query in indexes:
                cursor.execute(index_query)
            
            logger.info("Created all indexes")
            print("✓ Database schema initialized successfully!")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

# ============================================================================
# RECRUITER JOBS OPERATIONS
# ============================================================================
def create_job_posting(recruiter_id: str, job_data: Dict[str, Any]) -> int:
    """
    Create a new job posting
    Args:
        recruiter_id: ID of the recruiter
        job_data: Dictionary containing job details
    Returns: job_id of the created posting
    """
    try:
        with DatabaseManager.get_db_cursor(commit=True) as cursor:
            query = """
            INSERT INTO recruiter_jobs (
                recruiter_id, job_title, job_description, 
                skills_required, experience_required_years, 
                salary_range_min, salary_range_max, location,
                employment_type, industry, job_category,
                required_qualifications
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING job_id;
            """
            
            cursor.execute(query, (
                recruiter_id,
                job_data.get('job_title'),
                job_data.get('job_description'),
                Json(job_data.get('skills_required', [])),
                job_data.get('experience_required_years', 0),
                job_data.get('salary_range_min'),
                job_data.get('salary_range_max'),
                job_data.get('location'),
                job_data.get('employment_type'),
                job_data.get('industry'),
                job_data.get('job_category'),
                job_data.get('required_qualifications')
            ))
            
            job_id = cursor.fetchone()['job_id']
            logger.info(f"Created job posting: job_id={job_id}")
            return job_id
    except Exception as e:
        logger.error(f"Failed to create job posting: {str(e)}")
        raise

def store_job_embedding(job_id: int, embedding: List[float]) -> None:
    """
    Store job embedding for a job posting
    Args:
        job_id: ID of the job
        embedding: List of floats representing the embedding vector
    """
    try:
        with DatabaseManager.get_db_cursor(commit=True) as cursor:
            query = """
            UPDATE recruiter_jobs 
            SET job_embedding = %s, updated_at = CURRENT_TIMESTAMP
            WHERE job_id = %s;
            """
            cursor.execute(query, (Json(embedding), job_id))
            logger.info(f"Stored embedding for job_id={job_id}")
    except Exception as e:
        logger.error(f"Failed to store job embedding: {str(e)}")
        raise

def get_job_by_id(job_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve a job posting by ID
    Args:
        job_id: ID of the job
    Returns: Dictionary with job details or None if not found
    """
    try:
        with DatabaseManager.get_db_cursor(commit=False) as cursor:
            query = "SELECT * FROM recruiter_jobs WHERE job_id = %s;"
            cursor.execute(query, (job_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
    except Exception as e:
        logger.error(f"Failed to retrieve job: {str(e)}")
        raise

# ============================================================================
# CANDIDATE PROFILES OPERATIONS
# ============================================================================
def create_candidate_profile(candidate_data: Dict[str, Any]) -> int:
    """
    Create a new candidate profile
    Args:
        candidate_data: Dictionary containing candidate details
    Returns: candidate_id of the created profile
    """
    try:
        with DatabaseManager.get_db_cursor(commit=True) as cursor:
            query = """
            INSERT INTO candidate_profiles (
                candidate_name, email_address, phone_number,
                current_location, parsed_resume_data, skills,
                years_of_experience, current_cgpa, latest_company,
                latest_role_title, education_degree, education_institute,
                education_branch, notice_period_days, work_authorization,
                preferred_roles, employment_type_preference
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING candidate_id;
            """
            
            cursor.execute(query, (
                candidate_data.get('candidate_name'),
                candidate_data.get('email_address'),
                candidate_data.get('phone_number'),
                candidate_data.get('current_location'),
                Json(candidate_data.get('parsed_resume_data', {})),
                Json(candidate_data.get('skills', [])),
                candidate_data.get('years_of_experience', 0),
                candidate_data.get('current_cgpa', 0.0),
                candidate_data.get('latest_company'),
                candidate_data.get('latest_role_title'),
                candidate_data.get('education_degree'),
                candidate_data.get('education_institute'),
                candidate_data.get('education_branch'),
                candidate_data.get('notice_period_days'),
                candidate_data.get('work_authorization'),
                Json(candidate_data.get('preferred_roles', [])),
                candidate_data.get('employment_type_preference')
            ))
            
            candidate_id = cursor.fetchone()['candidate_id']
            logger.info(f"Created candidate profile: candidate_id={candidate_id}")
            return candidate_id
    except Exception as e:
        logger.error(f"Failed to create candidate profile: {str(e)}")
        raise

def store_candidate_embedding(candidate_id: int, embedding: List[float]) -> None:
    """
    Store candidate profile embedding
    Args:
        candidate_id: ID of the candidate
        embedding: List of floats representing the embedding vector
    """
    try:
        with DatabaseManager.get_db_cursor(commit=True) as cursor:
            query = """
            UPDATE candidate_profiles 
            SET profile_embedding = %s, last_updated = CURRENT_TIMESTAMP
            WHERE candidate_id = %s;
            """
            cursor.execute(query, (Json(embedding), candidate_id))
            logger.info(f"Stored embedding for candidate_id={candidate_id}")
    except Exception as e:
        logger.error(f"Failed to store candidate embedding: {str(e)}")
        raise

def get_candidate_by_id(candidate_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve a candidate profile by ID
    Args:
        candidate_id: ID of the candidate
    Returns: Dictionary with candidate details or None if not found
    """
    try:
        with DatabaseManager.get_db_cursor(commit=False) as cursor:
            query = "SELECT * FROM candidate_profiles WHERE candidate_id = %s;"
            cursor.execute(query, (candidate_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
    except Exception as e:
        logger.error(f"Failed to retrieve candidate: {str(e)}")
        raise

def get_all_active_candidates() -> List[Dict[str, Any]]:
    """
    Retrieve all active candidate profiles
    Returns: List of candidate dictionaries
    """
    try:
        with DatabaseManager.get_db_cursor(commit=False) as cursor:
            query = "SELECT * FROM candidate_profiles WHERE status = 'active';"
            cursor.execute(query)
            results = cursor.fetchall()
            return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Failed to retrieve candidates: {str(e)}")
        raise

# ============================================================================
# MATCHING RESULTS OPERATIONS
# ============================================================================
def store_match_result(match_data: Dict[str, Any]) -> int:
    """
    Store a matching result
    Args:
        match_data: Dictionary containing match details
    Returns: match_id of the created record
    """
    try:
        with DatabaseManager.get_db_cursor(commit=True) as cursor:
            query = """
            INSERT INTO matching_results (
                job_id, candidate_id, cosine_similarity_score,
                match_percentage, skill_match_score,
                experience_match_score, education_match_score,
                location_match_score, final_weighted_score,
                match_details
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING match_id;
            """
            
            cursor.execute(query, (
                match_data.get('job_id'),
                match_data.get('candidate_id'),
                match_data.get('cosine_similarity_score'),
                match_data.get('match_percentage'),
                match_data.get('skill_match_score', 0),
                match_data.get('experience_match_score', 0),
                match_data.get('education_match_score', 0),
                match_data.get('location_match_score', 0),
                match_data.get('final_weighted_score'),
                Json(match_data.get('match_details', {}))
            ))
            
            match_id = cursor.fetchone()['match_id']
            logger.info(f"Stored match result: match_id={match_id}")
            return match_id
    except Exception as e:
        logger.error(f"Failed to store match result: {str(e)}")
        raise

def get_matches_for_job(job_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Retrieve all matches for a specific job
    Args:
        job_id: ID of the job
        limit: Maximum number of results
    Returns: List of match dictionaries sorted by score
    """
    try:
        with DatabaseManager.get_db_cursor(commit=False) as cursor:
            query = """
            SELECT m.*, c.candidate_name, c.email_address
            FROM matching_results m
            JOIN candidate_profiles c ON m.candidate_id = c.candidate_id
            WHERE m.job_id = %s AND m.match_status = 'active'
            ORDER BY m.final_weighted_score DESC
            LIMIT %s;
            """
            cursor.execute(query, (job_id, limit))
            results = cursor.fetchall()
            return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Failed to retrieve job matches: {str(e)}")
        raise

def get_match_history(candidate_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Retrieve match history for a specific candidate
    Args:
        candidate_id: ID of the candidate
        limit: Maximum number of results
    Returns: List of match dictionaries with job details
    """
    try:
        with DatabaseManager.get_db_cursor(commit=False) as cursor:
            query = """
            SELECT m.*, j.job_title, j.job_description, j.recruiter_id
            FROM matching_results m
            JOIN recruiter_jobs j ON m.job_id = j.job_id
            WHERE m.candidate_id = %s
            ORDER BY m.final_weighted_score DESC
            LIMIT %s;
            """
            cursor.execute(query, (candidate_id, limit))
            results = cursor.fetchall()
            return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Failed to retrieve candidate matches: {str(e)}")
        raise
