# ============================================================================
# CANDIDATE-JOB MATCHING ROUTER
# Handles matching operations: find candidates for jobs, match analysis
# ============================================================================
import os
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from auth import validate_api_key
from database import (
    get_job_by_id,
    get_candidate_by_id,
    get_all_active_candidates,
    store_match_result,
    get_matches_for_job,
    get_match_history,
    DatabaseManager
)
from embedding_utils import (
    find_top_k_matches,
    calculate_composite_match_score,
    cosine_similarity,
    calculate_skill_match_score,
    calculate_experience_match_score,
    calculate_education_match_score,
    calculate_location_match_score
)
from config import DEFAULT_TOP_K, MIN_SIMILARITY_THRESHOLD
from dotenv import load_dotenv
import logging
from datetime import datetime

load_dotenv()
logger = logging.getLogger(__name__)

# ============================================================================
# PYDANTIC MODELS FOR REQUEST/RESPONSE
# ============================================================================
class FindMatchesRequest(BaseModel):
    """Request model for finding matching candidates"""
    job_id: int = Field(..., description="ID of the job posting")
    top_k: int = Field(
        default=DEFAULT_TOP_K,
        ge=1,
        le=100,
        description="Number of top matches to return"
    )
    min_threshold: Optional[float] = Field(
        default=MIN_SIMILARITY_THRESHOLD,
        ge=0,
        le=1,
        description="Minimum similarity threshold (0-1)"
    )

class MatchScoreDetail(BaseModel):
    """Detailed match score breakdown"""
    cosine_similarity_score: float
    skill_match_score: float
    experience_match_score: float
    education_match_score: float
    location_match_score: float
    final_weighted_score: float
    match_percentage: float

class CandidateMatch(BaseModel):
    """Single candidate match result"""
    candidate_id: int
    candidate_name: str
    email_address: Optional[str]
    scores: MatchScoreDetail
    candidate_summary: Dict[str, Any]

class MatchesResponse(BaseModel):
    """Response model for matches"""
    job_id: int
    total_matches_found: int
    top_k_requested: int
    matches: List[CandidateMatch]
    timestamp: str

class GetCandidateMatchesRequest(BaseModel):
    """Request for getting matches for a candidate"""
    candidate_id: int = Field(..., description="ID of the candidate")
    top_k: int = Field(
        default=DEFAULT_TOP_K,
        ge=1,
        le=100,
        description="Number of top matches to return"
    )

# ============================================================================
# ROUTER SETUP
# ============================================================================
router = APIRouter(
    prefix="/match",
    tags=["Matching Operations"],
    dependencies=[Depends(validate_api_key)]
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def prepare_candidate_summary(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare a clean summary of candidate for response"""
    return {
        'name': candidate.get('candidate_name'),
        'location': candidate.get('current_location'),
        'experience': candidate.get('years_of_experience'),
        'degree': candidate.get('education_degree'),
        'cgpa': candidate.get('current_cgpa'),
        'skills': candidate.get('skills', []),
        'latest_company': candidate.get('latest_company'),
        'latest_role': candidate.get('latest_role_title')
    }

def calculate_and_store_match(
    job_id: int,
    candidate_id: int,
    job_data: Dict[str, Any],
    candidate_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate match score and store in database
    Returns match scores
    """
    try:
        # Get embeddings
        job_embedding = job_data.get('job_embedding')
        candidate_embedding = candidate_data.get('profile_embedding')
        
        if not job_embedding or not candidate_embedding:
            logger.warning(f"Missing embeddings for job {job_id} or candidate {candidate_id}")
            return None
        
        # Calculate scores
        scores = calculate_composite_match_score(
            job_embedding,
            candidate_embedding,
            job_skills=job_data.get('skills_required', []),
            candidate_skills=candidate_data.get('skills', []),
            job_exp_required=job_data.get('experience_required_years', 0),
            candidate_exp=candidate_data.get('years_of_experience', 0),
            job_qualifications=job_data.get('required_qualifications', ''),
            candidate_degree=candidate_data.get('education_degree', ''),
            candidate_cgpa=candidate_data.get('current_cgpa'),
            job_location=job_data.get('location', ''),
            candidate_location=candidate_data.get('current_location', '')
        )
        
        # Store in database
        match_data = {
            'job_id': job_id,
            'candidate_id': candidate_id,
            'cosine_similarity_score': scores['cosine_similarity_score'],
            'match_percentage': scores['match_percentage'],
            'skill_match_score': scores['skill_match_score'],
            'experience_match_score': scores['experience_match_score'],
            'education_match_score': scores['education_match_score'],
            'location_match_score': scores['location_match_score'],
            'final_weighted_score': scores['final_weighted_score'],
            'match_details': {
                'job_title': job_data.get('job_title'),
                'candidate_name': candidate_data.get('candidate_name'),
                'matched_at': datetime.now().isoformat()
            }
        }
        
        store_match_result(match_data)
        return scores
        
    except Exception as e:
        logger.error(f"Error calculating/storing match: {str(e)}")
        return None

# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/find-candidates", response_model=Dict[str, Any])
def find_matching_candidates(request: FindMatchesRequest):
    """
    Find top matching candidates for a job posting
    
    **Algorithm:**
    1. Retrieve job posting and its embedding
    2. Fetch all active candidate profiles with embeddings
    3. Calculate composite match scores for each candidate:
       - Cosine similarity on embeddings (10%)
       - Skill match score (35%)
       - Experience match score (25%)
       - Education match score (20%)
       - Location match score (10%)
    4. Apply minimum threshold filter
    5. Sort by final weighted score
    6. Return top K matches
    7. Store all matches in database
    
    **Formulas:**
    - Cosine Similarity: cos(θ) = (A · B) / (||A|| × ||B||)
    - Skill Match: matched_skills / required_skills
    - Experience Match: Penalizes if underexperienced
    - Education Match: Degree level + CGPA consideration
    - Location Match: Exact/partial/regional matching
    - Final Score: Weighted sum of all factors
    
    **Parameters:**
    - job_id: ID of the job posting
    - top_k: Number of top matches to return (default: 10, max: 100)
    - min_threshold: Minimum match score threshold (default: 0.4, range: 0-1)
    
    **Response:**
    Returns list of matching candidates with detailed score breakdown
    """
    try:
        # Retrieve job
        job = get_job_by_id(request.job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job ID {request.job_id} not found")
        
        job_dict = dict(job)
        
        # Check if job has embedding
        if not job_dict.get('job_embedding'):
            raise HTTPException(
                status_code=400,
                detail=f"Job must have embedding. Run /recruiter/jobs/embed first for job_id {request.job_id}"
            )
        
        logger.info(f"Finding matches for job_id={request.job_id}, top_k={request.top_k}")
        
        # Get all active candidates
        candidates = get_all_active_candidates()
        
        # Filter candidates with embeddings
        candidates_with_embeddings = [
            c for c in candidates if c.get('profile_embedding')
        ]
        
        if not candidates_with_embeddings:
            logger.warning(f"No candidates with embeddings found")
            return {
                'status': 'success',
                'job_id': request.job_id,
                'total_candidates_checked': 0,
                'candidates_with_embeddings': 0,
                'matches_found': [],
                'message': 'No candidates with embeddings available'
            }
        
        logger.info(f"Checking {len(candidates_with_embeddings)} candidates with embeddings")
        
        # Calculate matches
        matches = find_top_k_matches(
            job_embedding=job_dict['job_embedding'],
            candidates=candidates_with_embeddings,
            job_data=job_dict,
            k=request.top_k,
            min_threshold=request.min_threshold or MIN_SIMILARITY_THRESHOLD
        )
        
        # Store matches in database
        stored_count = 0
        for match in matches:
            try:
                candidate = next(
                    (c for c in candidates if c['candidate_id'] == match['candidate_id']),
                    None
                )
                if candidate:
                    calculate_and_store_match(
                        request.job_id,
                        match['candidate_id'],
                        job_dict,
                        dict(candidate)
                    )
                    stored_count += 1
            except Exception as e:
                logger.error(f"Error storing match: {str(e)}")
        
        logger.info(f"Stored {stored_count} matches in database")
        
        # Prepare response
        matches_response = []
        for match in matches:
            candidate = next(
                (c for c in candidates if c['candidate_id'] == match['candidate_id']),
                None
            )
            
            if candidate:
                matches_response.append({
                    'candidate_id': match['candidate_id'],
                    'candidate_name': match.get('candidate_name'),
                    'email_address': match.get('email_address'),
                    'scores': {
                        'cosine_similarity_score': match['cosine_similarity_score'],
                        'skill_match_score': match['skill_match_score'],
                        'experience_match_score': match['experience_match_score'],
                        'education_match_score': match['education_match_score'],
                        'location_match_score': match['location_match_score'],
                        'final_weighted_score': match['final_weighted_score'],
                        'match_percentage': match['match_percentage']
                    },
                    'candidate_summary': prepare_candidate_summary(candidate)
                })
        
        return {
            'status': 'success',
            'job_id': request.job_id,
            'job_title': job_dict.get('job_title'),
            'total_candidates_checked': len(candidates_with_embeddings),
            'matches_found': len(matches_response),
            'top_k_requested': request.top_k,
            'min_threshold_used': request.min_threshold or MIN_SIMILARITY_THRESHOLD,
            'matches': matches_response,
            'timestamp': datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Matching failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Matching failed: {str(e)}")

@router.post("/find-jobs", response_model=Dict[str, Any])
def find_matching_jobs(request: GetCandidateMatchesRequest):
    """
    Find top matching job opportunities for a candidate
    
    **Parameters:**
    - candidate_id: ID of the candidate
    - top_k: Number of top matches to return
    
    **Response:**
    Returns list of matching jobs with detailed score breakdown
    """
    try:
        # Retrieve candidate
        candidate = get_candidate_by_id(request.candidate_id)
        
        if not candidate:
            raise HTTPException(status_code=404, detail=f"Candidate ID {request.candidate_id} not found")
        
        candidate_dict = dict(candidate)
        
        # Check if candidate has embedding
        if not candidate_dict.get('profile_embedding'):
            raise HTTPException(
                status_code=400,
                detail=f"Candidate must have embedding. Run /candidate/profile/embed first"
            )
        
        logger.info(f"Finding job matches for candidate_id={request.candidate_id}")
        
        # Get all active jobs with embeddings
        with DatabaseManager.get_db_cursor(commit=False) as cursor:
            cursor.execute(
                "SELECT * FROM recruiter_jobs WHERE status = 'active' AND job_embedding IS NOT NULL"
            )
            jobs = [dict(row) for row in cursor.fetchall()]
        
        if not jobs:
            return {
                'status': 'success',
                'candidate_id': request.candidate_id,
                'jobs_with_embeddings': 0,
                'matches_found': [],
                'message': 'No active jobs with embeddings available'
            }
        
        logger.info(f"Checking {len(jobs)} jobs with embeddings")
        
        # Calculate matches for each job
        matches = []
        
        for job in jobs:
            try:
                scores = calculate_composite_match_score(
                    job['job_embedding'],
                    candidate_dict['profile_embedding'],
                    job_skills=job.get('skills_required', []),
                    candidate_skills=candidate_dict.get('skills', []),
                    job_exp_required=job.get('experience_required_years', 0),
                    candidate_exp=candidate_dict.get('years_of_experience', 0),
                    job_qualifications=job.get('required_qualifications', ''),
                    candidate_degree=candidate_dict.get('education_degree', ''),
                    candidate_cgpa=candidate_dict.get('current_cgpa'),
                    job_location=job.get('location', ''),
                    candidate_location=candidate_dict.get('current_location', '')
                )
                
                if scores['final_weighted_score'] >= MIN_SIMILARITY_THRESHOLD:
                    matches.append({
                        'job_id': job['job_id'],
                        'job_title': job['job_title'],
                        'recruiter_id': job['recruiter_id'],
                        'location': job.get('location'),
                        'experience_required': job.get('experience_required_years'),
                        'scores': scores
                    })
            except Exception as e:
                logger.error(f"Error matching job {job['job_id']}: {str(e)}")
        
        # Sort by weighted score
        matches.sort(key=lambda x: x['scores']['final_weighted_score'], reverse=True)
        
        return {
            'status': 'success',
            'candidate_id': request.candidate_id,
            'candidate_name': candidate_dict.get('candidate_name'),
            'total_jobs_checked': len(jobs),
            'matches_found': len(matches),
            'top_k_requested': request.top_k,
            'matches': matches[:request.top_k],
            'timestamp': datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Job matching failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Job matching failed: {str(e)}")

@router.get("/job/{job_id}/results", response_model=Dict[str, Any])
def get_job_matches(
    job_id: int,
    limit: int = Query(50, ge=1, le=200)
):
    """
    Retrieve stored matching results for a specific job
    
    **Parameters:**
    - job_id: ID of the job
    - limit: Maximum number of results
    
    **Response:**
    Returns all stored matches for this job sorted by score
    """
    try:
        job = get_job_by_id(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job ID {job_id} not found")
        
        matches = get_matches_for_job(job_id, limit)
        
        return {
            'status': 'success',
            'job_id': job_id,
            'job_title': dict(job).get('job_title'),
            'total_matches': len(matches),
            'matches': matches,
            'retrieved_at': datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve job matches: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")

@router.get("/candidate/{candidate_id}/results", response_model=Dict[str, Any])
def get_candidate_matches(
    candidate_id: int,
    limit: int = Query(50, ge=1, le=200)
):
    """
    Retrieve stored matching history for a specific candidate
    
    **Parameters:**
    - candidate_id: ID of the candidate
    - limit: Maximum number of results
    
    **Response:**
    Returns all stored matches for this candidate
    """
    try:
        candidate = get_candidate_by_id(candidate_id)
        
        if not candidate:
            raise HTTPException(status_code=404, detail=f"Candidate ID {candidate_id} not found")
        
        matches = get_match_history(candidate_id, limit)
        
        return {
            'status': 'success',
            'candidate_id': candidate_id,
            'candidate_name': dict(candidate).get('candidate_name'),
            'total_matches': len(matches),
            'matches': matches,
            'retrieved_at': datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve candidate matches: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")

@router.get("/health", response_model=Dict[str, Any])
def matching_health_check():
    """
    Health check endpoint for matching service
    
    **Response:**
    Returns service status and statistics
    """
    try:
        with DatabaseManager.get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM matching_results")
            total_matches = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM recruiter_jobs WHERE job_embedding IS NOT NULL")
            jobs_with_embeddings = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM candidate_profiles WHERE profile_embedding IS NOT NULL")
            candidates_with_embeddings = cursor.fetchone()['count']
        
        return {
            'status': 'healthy',
            'service': 'matching-service',
            'total_matches_stored': total_matches,
            'jobs_with_embeddings': jobs_with_embeddings,
            'candidates_with_embeddings': candidates_with_embeddings
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Service health check failed")
