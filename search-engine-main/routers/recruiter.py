# ============================================================================
# RECRUITER JOB POSTING ROUTER
# Handles recruiter operations: create jobs, embed jobs, manage listings
# ============================================================================
import os
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from auth import validate_api_key
from database import (
    initialize_database,
    create_job_posting,
    get_job_by_id,
    store_job_embedding,
    DatabaseManager
)
from embedding_utils import generate_job_embedding
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

# ============================================================================
# PYDANTIC MODELS FOR REQUEST/RESPONSE
# ============================================================================
class JobSkill(BaseModel):
    """Model for job skills"""
    skill_name: str
    proficiency_level: Optional[str] = "intermediate"  # beginner, intermediate, expert
    years_required: Optional[float] = 0

class SalaryRange(BaseModel):
    """Model for salary range"""
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    currency: Optional[str] = "INR"

class CreateJobRequest(BaseModel):
    """Request model for creating a job posting"""
    recruiter_id: str = Field(..., description="Unique ID of the recruiter")
    job_title: str = Field(..., description="Title of the job position")
    job_description: str = Field(..., description="Detailed job description")
    
    skills_required: List[str] = Field(
        default=[],
        description="List of required skills"
    )
    experience_required_years: float = Field(
        default=0,
        ge=0,
        description="Years of experience required"
    )
    salary_range_min: Optional[int] = Field(default=None, description="Minimum salary")
    salary_range_max: Optional[int] = Field(default=None, description="Maximum salary")
    
    location: str = Field(..., description="Job location")
    employment_type: str = Field(
        default="full-time",
        description="Type: full-time, part-time, contract, temporary"
    )
    industry: Optional[str] = Field(default=None, description="Industry sector")
    job_category: Optional[str] = Field(default=None, description="Job category")
    required_qualifications: Optional[str] = Field(
        default=None,
        description="Specific qualifications required"
    )

class JobResponse(BaseModel):
    """Response model for job operations"""
    job_id: int
    recruiter_id: str
    job_title: str
    job_description: str
    skills_required: List[str]
    experience_required_years: float
    location: str
    employment_type: str
    industry: Optional[str] = None
    job_category: Optional[str] = None
    status: str
    created_at: str = None
    updated_at: str = None
    embedding_generated: bool = False

class EmbedJobRequest(BaseModel):
    """Request model for embedding a job"""
    job_id: int = Field(..., description="ID of the job to embed")

# ============================================================================
# ROUTER SETUP
# ============================================================================
router = APIRouter(
    prefix="/recruiter",
    tags=["Recruiter Operations"],
    dependencies=[Depends(validate_api_key)]
)

# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/jobs/create", response_model=Dict[str, Any])
def create_job(request: CreateJobRequest):
    """
    Create a new job posting
    
    **Parameters:**
    - recruiter_id: Unique identifier of the recruiter
    - job_title: Position title
    - job_description: Detailed job description
    - skills_required: List of required technical skills
    - experience_required_years: Minimum years of experience needed
    - location: Job location
    - employment_type: Full-time, part-time, contract, etc.
    - industry: Industry sector (optional)
    - job_category: Job category (optional)
    - required_qualifications: Specific educational qualifications (optional)
    
    **Response:**
    Returns job_id and confirmation of creation
    """
    try:
        job_data = {
            'job_title': request.job_title,
            'job_description': request.job_description,
            'skills_required': request.skills_required,
            'experience_required_years': request.experience_required_years,
            'salary_range_min': request.salary_range_min,
            'salary_range_max': request.salary_range_max,
            'location': request.location,
            'employment_type': request.employment_type,
            'industry': request.industry,
            'job_category': request.job_category,
            'required_qualifications': request.required_qualifications
        }
        
        job_id = create_job_posting(request.recruiter_id, job_data)
        
        logger.info(f"Job created successfully: job_id={job_id}, recruiter_id={request.recruiter_id}")
        
        return {
            'status': 'success',
            'job_id': job_id,
            'message': f'Job posting created successfully. Job ID: {job_id}',
            'next_step': 'Post to /recruiter/jobs/embed to generate embeddings'
        }
        
    except Exception as e:
        logger.error(f"Failed to create job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Job creation failed: {str(e)}")

@router.post("/jobs/embed", response_model=Dict[str, Any])
def embed_job(request: EmbedJobRequest):
    """
    Generate and store embedding for a job posting
    
    **Parameters:**
    - job_id: ID of the job to embed
    
    **Process:**
    1. Retrieve job from database
    2. Generate embedding using Gemini API
    3. Store embedding in database
    
    **Response:**
    Returns confirmation of embedding generation
    """
    try:
        # Retrieve job from database
        job = get_job_by_id(request.job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job ID {request.job_id} not found")
        
        # Generate embedding
        logger.info(f"Generating embedding for job_id={request.job_id}")
        embedding = generate_job_embedding(
            job['job_description'],
            job['job_title'],
            job['skills_required']
        )
        
        # Store embedding
        store_job_embedding(request.job_id, embedding)
        
        logger.info(f"Embedding stored successfully for job_id={request.job_id}")
        
        return {
            'status': 'success',
            'job_id': request.job_id,
            'embedding_dimension': len(embedding),
            'message': 'Job embedding generated and stored successfully'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Embedding generation failed for job_id={request.job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(e)}")

@router.get("/jobs/{job_id}", response_model=Dict[str, Any])
def get_job(job_id: int):
    """
    Retrieve a specific job posting by ID
    
    **Parameters:**
    - job_id: ID of the job to retrieve
    
    **Response:**
    Returns complete job details including embedding status
    """
    try:
        job = get_job_by_id(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job ID {job_id} not found")
        
        # Convert job dict and remove embedding for cleaner response (if very large)
        job_dict = dict(job)
        has_embedding = job_dict.get('job_embedding') is not None
        if has_embedding:
            job_dict['job_embedding'] = None  # Don't return huge embedding array
        
        return {
            **job_dict,
            'embedding_generated': has_embedding
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Job retrieval failed: {str(e)}")

@router.get("/jobs", response_model=Dict[str, Any])
def list_recruiter_jobs(
    recruiter_id: str = Query(..., description="Recruiter ID to filter by"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of jobs to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    List all job postings for a recruiter
    
    **Parameters:**
    - recruiter_id: Filter jobs by recruiter ID
    - limit: Number of jobs to return (max 200)
    - offset: Pagination offset
    
    **Response:**
    Returns list of job postings with pagination info
    """
    try:
        with DatabaseManager.get_db_cursor(commit=False) as cursor:
            # Get total count
            cursor.execute(
                "SELECT COUNT(*) as count FROM recruiter_jobs WHERE recruiter_id = %s",
                (recruiter_id,)
            )
            total_count = cursor.fetchone()['count']
            
            # Get paginated results
            cursor.execute(
                """SELECT job_id, recruiter_id, job_title, experience_required_years, 
                   location, employment_type, status, created_at
                   FROM recruiter_jobs 
                   WHERE recruiter_id = %s 
                   ORDER BY created_at DESC 
                   LIMIT %s OFFSET %s""",
                (recruiter_id, limit, offset)
            )
            
            jobs = [dict(row) for row in cursor.fetchall()]
            
            return {
                'status': 'success',
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'jobs': jobs
            }
            
    except Exception as e:
        logger.error(f"Failed to list jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Job listing failed: {str(e)}")

@router.put("/jobs/{job_id}/status", response_model=Dict[str, Any])
def update_job_status(
    job_id: int,
    status: str = Query(..., description="New status: active or inactive")
):
    """
    Update job posting status
    
    **Parameters:**
    - job_id: ID of the job
    - status: New status (active or inactive)
    
    **Response:**
    Returns confirmation of status update
    """
    try:
        valid_statuses = ['active', 'inactive', 'closed', 'expired']
        
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        with DatabaseManager.get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "UPDATE recruiter_jobs SET status = %s, updated_at = CURRENT_TIMESTAMP WHERE job_id = %s",
                (status, job_id)
            )
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail=f"Job ID {job_id} not found")
        
        logger.info(f"Job status updated: job_id={job_id}, status={status}")
        
        return {
            'status': 'success',
            'job_id': job_id,
            'new_status': status,
            'message': f'Job status updated to {status}'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update job status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Job status update failed: {str(e)}")

@router.get("/health", response_model=Dict[str, Any])
def recruiter_health_check():
    """
    Health check endpoint for recruiter service
    
    **Response:**
    Returns service status and total job count
    """
    try:
        with DatabaseManager.get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM recruiter_jobs WHERE status = 'active'")
            active_jobs = cursor.fetchone()['count']
        
        return {
            'status': 'healthy',
            'service': 'recruiter-jobs',
            'total_active_jobs': active_jobs
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Service health check failed")

# ============================================================================
# STARTUP FUNCTION
# ============================================================================
async def on_recruiter_startup():
    """Initialize database schema on application startup"""
    try:
        initialize_database()
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        # Don't raise - allow app to start even if schema exists
