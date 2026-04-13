# ============================================================================
# CANDIDATE PROFILE ROUTER
# Handles candidate operations: parse resumes, embed profiles, manage profiles
# ============================================================================
import os
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from auth import validate_api_key
from database import (
    create_candidate_profile,
    get_candidate_by_id,
    store_candidate_embedding,
    get_all_active_candidates,
    DatabaseManager
)
from embedding_utils import generate_candidate_embedding
from google import genai
from google.genai import types
from dotenv import load_dotenv
import json
import logging

load_dotenv()
logger = logging.getLogger(__name__)

# Initialize Gemini client
genai_client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

# ============================================================================
# PYDANTIC MODELS FOR REQUEST/RESPONSE
# ============================================================================
class ParseResumeRequest(BaseModel):
    """Request model for parsing resume text"""
    resume_text: str = Field(..., description="Raw resume text to parse")

class CandidateProfileData(BaseModel):
    """Model for candidate profile information"""
    candidate_name: str
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    current_location: Optional[str] = None
    
    parsed_resume_data: Optional[Dict[str, Any]] = None
    skills: Optional[List[str]] = None
    years_of_experience: Optional[float] = 0
    current_cgpa: Optional[float] = None
    latest_company: Optional[str] = None
    latest_role_title: Optional[str] = None
    education_degree: Optional[str] = None
    education_institute: Optional[str] = None
    education_branch: Optional[str] = None
    
    notice_period_days: Optional[int] = None
    work_authorization: Optional[str] = None
    preferred_roles: Optional[List[str]] = None
    employment_type_preference: Optional[str] = None

class CreateCandidateRequest(BaseModel):
    """Request model for creating a candidate profile"""
    candidate_name: str = Field(..., description="Full name of the candidate")
    email_address: str = Field(..., description="Email address")
    phone_number: Optional[str] = Field(None, description="Phone number")
    current_location: str = Field(..., description="Current location")
    
    skills: List[str] = Field(default=[], description="List of skills")
    years_of_experience: float = Field(default=0, ge=0, description="Years of experience")
    current_cgpa: Optional[float] = Field(None, ge=0, le=10, description="CGPA (0-10)")
    
    latest_company: Optional[str] = Field(None, description="Latest company worked for")
    latest_role_title: Optional[str] = Field(None, description="Latest job title")
    
    education_degree: str = Field(..., description="Degree (e.g., B.Tech, MBA)")
    education_institute: str = Field(..., description="Name of institution")
    education_branch: Optional[str] = Field(None, description="Branch/Stream of study")
    
    notice_period_days: Optional[int] = Field(None, description="Notice period in days")
    work_authorization: Optional[str] = Field(None, description="Work authorization status")
    
    preferred_roles: Optional[List[str]] = Field(default=[], description="Preferred job roles")
    employment_type_preference: Optional[str] = Field(None, description="Preferred employment type")

class EmbedCandidateRequest(BaseModel):
    """Request model for embedding a candidate"""
    candidate_id: int = Field(..., description="ID of the candidate to embed")

class CandidateResponse(BaseModel):
    """Response model for candidate operations"""
    candidate_id: int
    candidate_name: str
    email_address: Optional[str]
    current_location: str
    years_of_experience: float
    current_cgpa: Optional[float]
    education_degree: str
    status: str
    embedding_generated: bool

# ============================================================================
# ROUTER SETUP
# ============================================================================
router = APIRouter(
    prefix="/candidate",
    tags=["Candidate Operations"],
    dependencies=[Depends(validate_api_key)]
)

# ============================================================================
# RESUME PARSING FUNCTION
# ============================================================================
def parse_resume_with_gemini(resume_text: str) -> Dict[str, Any]:
    """
    Parse resume using Gemini API to extract structured information
    
    Args:
        resume_text: Raw resume text
    
    Returns:
        Structured resume data as dictionary
    """
    desired_structure = {
        "candidate_information": {
            "contact_details": {
                "full_name": "",
                "email_address": "",
                "phone_number": "",
                "current_location": ""
            },
            "education_snapshot": {
                "college_university": "",
                "degree_branch": "",
                "graduation_year": "",
                "cgpa_percentage": ""
            },
            "professional_summary": ""
        },
        "work_preferences": {
            "preferred_roles": "",
            "employment_type": "",
            "notice_period_availability": "",
            "work_authorization": ""
        },
        "experience_snapshot": {
            "latest_company": "",
            "role_title": "",
            "years_of_experience": "",
            "current_ctc": ""
        },
        "skills": [],
        "projects": [
            {
                "project_title": "",
                "description": "",
                "technologies_used": [],
                "role": "",
                "duration": "",
                "project_link": ""
            }
        ],
        "achievements_certifications": [
            {
                "title": "",
                "issuer": "",
                "year": "",
                "description": ""
            }
        ],
        "public_links": {
            "portfolio_website": "",
            "linkedin": "",
            "github_code_repo": "",
            "other_link": ""
        }
    }
    
    prompt = f"""
    You are a precise resume data extraction specialist.
    Analyze the following resume text and extract ALL the data to match the provided JSON structure EXACTLY.
    
    CRITICAL RULES:
    1. Extract EVERY piece of information from the resume
    2. If a field is not found in the resume, return null or an empty string (NOT "N/A")
    3. Do NOT invent or assume information
    4. For skills, return as a JSON array of strings: ["Python", "Java", "AWS"]
    5. Ensure years_of_experience is a NUMBER, not a string
    6. Output MUST be valid JSON only - no markdown, no explanation
    7. Return exactly this structure, nothing more or less
    
    Target JSON Structure:
    {json.dumps(desired_structure, indent=2)}
    
    RESUME TEXT:
    {resume_text} 
    
    IMPORTANT: Output ONLY valid JSON. Start with {{ and end with }}
    """
    
    try:
        response = genai_client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type='application/json'
            )
        )
        
        parsed_data = json.loads(response.text)
        logger.info("Resume parsed successfully")
        return parsed_data
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Resume parsing returned invalid JSON: {str(e)}")
    except Exception as e:
        logger.error(f"Resume parsing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Resume parsing failed: {str(e)}")

# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/profile/parse", response_model=Dict[str, Any])
def parse_resume(request: ParseResumeRequest):
    """
    Parse a resume text and extract structured information
    
    **Parameters:**
    - resume_text: Raw text from resume (can be copy-pasted)
    
    **Process:**
    1. Send resume to Gemini API for parsing
    2. Extract structured data following defined schema
    3. Return parsed JSON
    
    **Response:**
    Returns structured resume data with all fields populated
    """
    try:
        if not request.resume_text or len(request.resume_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Resume text must be at least 50 characters long"
            )
        
        parsed_data = parse_resume_with_gemini(request.resume_text)
        
        logger.info("Resume parsed successfully")
        
        return {
            'status': 'success',
            'parsed_data': parsed_data,
            'message': 'Resume parsed successfully. Review and create profile using /candidate/profile/create'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resume parsing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Resume parsing failed: {str(e)}")

@router.post("/profile/create", response_model=Dict[str, Any])
def create_candidate(request: CreateCandidateRequest):
    """
    Create a new candidate profile
    
    **Parameters:**
    - candidate_name: Full name
    - email_address: Email address
    - current_location: Current location
    - skills: List of skills
    - years_of_experience: Total years of experience
    - education_degree: Degree type (B.Tech, MBA, etc.)
    - education_institute: University/College name
    - And other profile details...
    
    **Response:**
    Returns candidate_id and confirmation of creation
    """
    try:
        candidate_data = {
            'candidate_name': request.candidate_name,
            'email_address': request.email_address,
            'phone_number': request.phone_number,
            'current_location': request.current_location,
            'skills': request.skills,
            'years_of_experience': request.years_of_experience,
            'current_cgpa': request.current_cgpa,
            'latest_company': request.latest_company,
            'latest_role_title': request.latest_role_title,
            'education_degree': request.education_degree,
            'education_institute': request.education_institute,
            'education_branch': request.education_branch,
            'notice_period_days': request.notice_period_days,
            'work_authorization': request.work_authorization,
            'preferred_roles': request.preferred_roles,
            'employment_type_preference': request.employment_type_preference
        }
        
        candidate_id = create_candidate_profile(candidate_data)
        
        logger.info(f"Candidate created: candidate_id={candidate_id}")
        
        return {
            'status': 'success',
            'candidate_id': candidate_id,
            'message': f'Candidate profile created successfully. ID: {candidate_id}',
            'next_step': 'Post to /candidate/profile/embed to generate embeddings'
        }
        
    except Exception as e:
        logger.error(f"Failed to create candidate: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Candidate creation failed: {str(e)}")

@router.post("/profile/embed", response_model=Dict[str, Any])
def embed_candidate(request: EmbedCandidateRequest):
    """
    Generate and store embedding for a candidate profile
    
    **Parameters:**
    - candidate_id: ID of the candidate
    
    **Process:**
    1. Retrieve candidate from database
    2. Generate embedding using Gemini API
    3. Store embedding in database
    
    **Response:**
    Returns confirmation of embedding generation
    """
    try:
        candidate = get_candidate_by_id(request.candidate_id)
        
        if not candidate:
            raise HTTPException(status_code=404, detail=f"Candidate ID {request.candidate_id} not found")
        
        logger.info(f"Generating embedding for candidate_id={request.candidate_id}")
        embedding = generate_candidate_embedding(dict(candidate))
        
        store_candidate_embedding(request.candidate_id, embedding)
        
        logger.info(f"Embedding stored successfully for candidate_id={request.candidate_id}")
        
        return {
            'status': 'success',
            'candidate_id': request.candidate_id,
            'embedding_dimension': len(embedding),
            'message': 'Candidate embedding generated and stored successfully'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Embedding generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(e)}")

@router.get("/profile/{candidate_id}", response_model=Dict[str, Any])
def get_candidate(candidate_id: int):
    """
    Retrieve a candidate profile by ID
    
    **Parameters:**
    - candidate_id: ID of the candidate
    
    **Response:**
    Returns complete candidate profile
    """
    try:
        candidate = get_candidate_by_id(candidate_id)
        
        if not candidate:
            raise HTTPException(status_code=404, detail=f"Candidate ID {candidate_id} not found")
        
        candidate_dict = dict(candidate)
        has_embedding = candidate_dict.get('profile_embedding') is not None
        if has_embedding:
            candidate_dict['profile_embedding'] = None
        
        return {
            **candidate_dict,
            'embedding_generated': has_embedding
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve candidate: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Candidate retrieval failed: {str(e)}")

@router.get("/profiles", response_model=Dict[str, Any])
def list_candidates(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of candidates"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    location: Optional[str] = Query(None, description="Filter by location")
):
    """
    List all candidate profiles
    
    **Parameters:**
    - limit: Number of candidates to return
    - offset: Pagination offset
    - location: Optional filter by location
    
    **Response:**
    Returns paginated list of candidates
    """
    try:
        with DatabaseManager.get_db_cursor(commit=False) as cursor:
            # Build query based on filters
            where_clause = "WHERE status = 'active'"
            params = []
            
            if location:
                where_clause += " AND current_location ILIKE %s"
                params.append(f"%{location}%")
            
            # Get total count
            cursor.execute(f"SELECT COUNT(*) as count FROM candidate_profiles {where_clause}", params)
            total_count = cursor.fetchone()['count']
            
            # Get paginated results
            query = f"""
                SELECT candidate_id, candidate_name, email_address, current_location,
                       years_of_experience, current_cgpa, education_degree, status
                FROM candidate_profiles
                {where_clause}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, params + [limit, offset])
            candidates = [dict(row) for row in cursor.fetchall()]
            
            return {
                'status': 'success',
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'candidates': candidates
            }
            
    except Exception as e:
        logger.error(f"Failed to list candidates: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Candidate listing failed: {str(e)}")

@router.put("/profile/{candidate_id}/status", response_model=Dict[str, Any])
def update_candidate_status(
    candidate_id: int,
    status: str = Query(..., description="New status: active or inactive")
):
    """
    Update candidate profile status
    
    **Parameters:**
    - candidate_id: ID of the candidate
    - status: New status (active or inactive)
    """
    try:
        valid_statuses = ['active', 'inactive', 'hired', 'rejected']
        
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        with DatabaseManager.get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "UPDATE candidate_profiles SET status = %s, last_updated = CURRENT_TIMESTAMP WHERE candidate_id = %s",
                (status, candidate_id)
            )
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail=f"Candidate ID {candidate_id} not found")
        
        logger.info(f"Candidate status updated: candidate_id={candidate_id}, status={status}")
        
        return {
            'status': 'success',
            'candidate_id': candidate_id,
            'new_status': status,
            'message': f'Candidate status updated to {status}'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update candidate status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status update failed: {str(e)}")

@router.get("/health", response_model=Dict[str, Any])
def candidate_health_check():
    """
    Health check endpoint for candidate service
    
    **Response:**
    Returns service status and total candidate count
    """
    try:
        candidates = get_all_active_candidates()
        
        return {
            'status': 'healthy',
            'service': 'candidate-profiles',
            'total_active_candidates': len(candidates)
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Service health check failed")
