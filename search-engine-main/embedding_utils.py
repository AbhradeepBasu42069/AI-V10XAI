# ============================================================================
# EMBEDDING AND MATCHING UTILITIES
# Handles Gemini embeddings, similarity calculations, and matching algorithm
# ============================================================================
from typing import List, Dict, Any, Tuple
import numpy as np
from google import genai
from google.genai import types
from config import (
    GEMINI_API_KEY, 
    EMBEDDING_MODEL, 
    EMBEDDING_DIMENSION,
    MATCHING_WEIGHTS,
    MIN_SIMILARITY_THRESHOLD,
    GEMINI_MODEL_FOR_GENERATION
)
from fastapi import HTTPException
import logging
import json
import re

logger = logging.getLogger(__name__)

# Initialize Gemini client
genai_client = genai.Client(api_key=GEMINI_API_KEY)

# ============================================================================
# EMBEDDING GENERATION
# ============================================================================
def generate_embedding(text: str, dimensionality: int = EMBEDDING_DIMENSION) -> List[float]:
    """
    Generate embedding vector using Gemini API
    Args:
        text: Text to embed
        dimensionality: Dimension of the embedding vector
    Returns: List of floats representing the embedding
    Raises: HTTPException if embedding generation fails
    """
    try:
        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")
        
        response = genai_client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text.strip(),
            config={'output_dimensionality': dimensionality}
        )
        
        embedding = response.embeddings[0].values
        logger.info(f"Generated embedding with dimension {len(embedding)}")
        return embedding
        
    except Exception as e:
        logger.error(f"Embedding generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(e)}")

def generate_job_embedding(job_description: str, job_title: str = "", skills: List[str] = None) -> List[float]:
    """
    Generate embedding specifically for job postings
    Combines job title, description, and skills for comprehensive embedding
    Args:
        job_description: Full job description text
        job_title: Title of the job
        skills: List of required skills
    Returns: Embedding vector
    """
    try:
        # Create a comprehensive job text representation
        job_text_parts = [job_title] if job_title else []
        job_text_parts.append(job_description)
        if skills:
            job_text_parts.append("Required Skills: " + ", ".join(skills))
        
        comprehensive_text = " ".join(job_text_parts)
        return generate_embedding(comprehensive_text)
        
    except Exception as e:
        logger.error(f"Job embedding generation failed: {str(e)}")
        raise

def generate_candidate_embedding(candidate_data: Dict[str, Any]) -> List[float]:
    """
    Generate embedding for candidate profile
    Creates a comprehensive markdown representation and embeds it
    Args:
        candidate_data: Dictionary with parsed candidate information
    Returns: Embedding vector
    """
    try:
        # Convert candidate data to readable text format
        text_parts = []
        
        # Extract key information
        if candidate_data.get('candidate_name'):
            text_parts.append(f"Name: {candidate_data['candidate_name']}")
        
        if candidate_data.get('years_of_experience'):
            text_parts.append(f"Experience: {candidate_data['years_of_experience']} years")
        
        if candidate_data.get('skills'):
            skills = candidate_data['skills']
            if isinstance(skills, list):
                text_parts.append(f"Skills: {', '.join(skills)}")
            elif isinstance(skills, dict):
                text_parts.append(f"Skills: {', '.join(skills.values())}")
        
        if candidate_data.get('latest_role_title'):
            text_parts.append(f"Latest Role: {candidate_data['latest_role_title']}")
        
        if candidate_data.get('latest_company'):
            text_parts.append(f"Latest Company: {candidate_data['latest_company']}")
        
        if candidate_data.get('education_degree'):
            degree_info = f"Degree: {candidate_data['education_degree']}"
            if candidate_data.get('education_branch'):
                degree_info += f" in {candidate_data['education_branch']}"
            text_parts.append(degree_info)
        
        if candidate_data.get('current_cgpa'):
            text_parts.append(f"CGPA: {candidate_data['current_cgpa']}")
        
        if candidate_data.get('preferred_roles'):
            roles = candidate_data['preferred_roles']
            if isinstance(roles, list):
                text_parts.append(f"Preferred Roles: {', '.join(roles)}")
        
        # Create comprehensive text
        comprehensive_text = " ".join(text_parts)
        
        if not comprehensive_text:
            comprehensive_text = "Candidate profile"
        
        return generate_embedding(comprehensive_text)
        
    except Exception as e:
        logger.error(f"Candidate embedding generation failed: {str(e)}")
        raise

# ============================================================================
# SIMILARITY CALCULATIONS
# ============================================================================
def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors
    Formula: cos(θ) = (A · B) / (||A|| × ||B||)
    
    Args:
        vec1: First vector
        vec2: Second vector
    Returns: Similarity score between -1 and 1
    """
    try:
        v1 = np.array(vec1, dtype=np.float32)
        v2 = np.array(vec2, dtype=np.float32)
        
        # Calculate dot product
        dot_product = np.dot(v1, v2)
        
        # Calculate norms
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        
        # Avoid division by zero
        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0
        
        similarity = dot_product / (norm_v1 * norm_v2)
        
        # Clamp to [-1, 1] to handle floating point errors
        similarity = np.clip(similarity, -1.0, 1.0)
        
        return float(similarity)
        
    except Exception as e:
        logger.error(f"Cosine similarity calculation failed: {str(e)}")
        return 0.0

def euclidean_distance(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate Euclidean distance between two vectors
    Formula: d = √(Σ(A[i] - B[i])²)
    
    Args:
        vec1: First vector
        vec2: Second vector
    Returns: Distance (non-negative)
    """
    try:
        v1 = np.array(vec1, dtype=np.float32)
        v2 = np.array(vec2, dtype=np.float32)
        
        distance = np.linalg.norm(v1 - v2)
        return float(distance)
        
    except Exception as e:
        logger.error(f"Euclidean distance calculation failed: {str(e)}")
        return float('inf')

# ============================================================================
# DETAILED MATCHING ALGORITHM
# ============================================================================
def calculate_skill_match_score(job_skills: List[str], candidate_skills: List[str]) -> float:
    """
    Calculate skill match score based on intersection
    Formula: matched_skills / total_required_skills
    
    Args:
        job_skills: List of required job skills
        candidate_skills: List of candidate skills
    Returns: Score between 0 and 1
    """
    try:
        if not job_skills:
            return 1.0  # No skills required
        
        # Convert to lowercase for comparison
        job_skills_lower = [s.lower().strip() for s in job_skills]
        candidate_skills_lower = [s.lower().strip() for s in candidate_skills]
        
        # Find matches (including partial matches)
        matched_count = 0
        for job_skill in job_skills_lower:
            for candidate_skill in candidate_skills_lower:
                if job_skill in candidate_skill or candidate_skill in job_skill:
                    matched_count += 1
                    break
        
        score = matched_count / len(job_skills)
        return min(score, 1.0)
        
    except Exception as e:
        logger.error(f"Skill match calculation failed: {str(e)}")
        return 0.5  # Default to neutral score

def calculate_experience_match_score(
    job_required_years: float, 
    candidate_years: float,
    tolerance: float = 2.0
) -> float:
    """
    Calculate experience match score
    Penalizes if candidate has significantly less experience
    Formula: 1 - (max(0, job_required - candidate_years) / (job_required + tolerance)) 
    
    Args:
        job_required_years: Years of experience required for the job
        candidate_years: Candidate's years of experience
        tolerance: Years of tolerance for being underexperienced
    Returns: Score between 0 and 1
    """
    try:
        if job_required_years == 0:
            return 1.0 if candidate_years >= 0 else 0.0
        
        if candidate_years >= job_required_years:
            return 1.0
        
        experience_gap = job_required_years - candidate_years
        
        # Score decreases based on experience gap
        if experience_gap <= tolerance:
            score = 1.0 - (experience_gap / (job_required_years + tolerance))
        else:
            score = max(0.0, 1.0 - (experience_gap / (job_required_years * 2)))
        
        return max(0.0, min(score, 1.0))
        
    except Exception as e:
        logger.error(f"Experience match calculation failed: {str(e)}")
        return 0.5

def calculate_education_match_score(
    job_qualifications: str,
    candidate_degree: str,
    candidate_cgpa: float = None
) -> float:
    """
    Calculate education match score based on degree level
    Formula: Weighted comparison of degree levels + CGPA bonus
    
    Args:
        job_qualifications: Required qualifications text
        candidate_degree: Candidate's degree
        candidate_cgpa: Candidate's CGPA (optional)
    Returns: Score between 0 and 1
    """
    try:
        base_score = 0.5  # Default score for some education
        
        # Check for degree match
        degree_keywords = {
            'phd': 1.0,
            'doctorate': 1.0,
            'master': 0.9,
            'mtech': 0.9,
            'mba': 0.85,
            'bachelor': 0.8,
            'btech': 0.8,
            'bsc': 0.75,
            'diploma': 0.6,
            'undergraduate': 0.75
        }
        
        job_qual_lower = job_qualifications.lower() if job_qualifications else ""
        candidate_degree_lower = candidate_degree.lower() if candidate_degree else ""
        
        # Find matching degree level
        score = 0.5
        for degree_type, degree_score in degree_keywords.items():
            if degree_type in candidate_degree_lower:
                if degree_type in job_qual_lower or job_qual_lower == "":
                    score = degree_score
                else:
                    # Lower score if degree type doesn't match requirements
                    score = degree_score * 0.7
                break
        
        # Add CGPA bonus if excellent
        if candidate_cgpa and candidate_cgpa >= 8.5:
            score = min(1.0, score + 0.1)
        
        return min(score, 1.0)
        
    except Exception as e:
        logger.error(f"Education match calculation failed: {str(e)}")
        return 0.5

def calculate_location_match_score(
    job_location: str,
    candidate_location: str,
    strict_match: bool = False
) -> float:
    """
    Calculate location match score
    Args:
        job_location: Job location
        candidate_location: Candidate's location
        strict_match: If True, require exact location; if False, be more flexible
    Returns: Score between 0 and 1
    """
    try:
        if not job_location or not candidate_location:
            return 0.5  # Neutral if no location info
        
        job_loc_lower = job_location.lower().strip()
        candidate_loc_lower = candidate_location.lower().strip()
        
        if job_loc_lower == candidate_loc_lower:
            return 1.0  # Exact match
        
        if not strict_match:
            # Check if location is mentioned in a larger area
            if job_loc_lower in candidate_loc_lower or candidate_loc_lower in job_loc_lower:
                return 0.8  # Partial match (same city/region)
            
            # Check for common keywords (country/state level)
            job_parts = job_loc_lower.split(',')
            candidate_parts = candidate_loc_lower.split(',')
            
            # If last part (usually country) matches
            if job_parts[-1].strip() == candidate_parts[-1].strip():
                return 0.6  # Same country/region
        
        return 0.3  # Different locations
        
    except Exception as e:
        logger.error(f"Location match calculation failed: {str(e)}")
        return 0.5

def calculate_composite_match_score(
    job_embedding: List[float],
    candidate_embedding: List[float],
    job_skills: List[str] = None,
    candidate_skills: List[str] = None,
    job_exp_required: float = 0,
    candidate_exp: float = 0,
    job_qualifications: str = "",
    candidate_degree: str = "",
    candidate_cgpa: float = None,
    job_location: str = "",
    candidate_location: str = ""
) -> Dict[str, float]:
    """
    Calculate comprehensive matching score using multiple factors
    
    Returns dictionary with:
    - cosine_similarity_score: Embedding similarity
    - skill_match_score: Skill alignment
    - experience_match_score: Experience alignment
    - education_match_score: Education alignment
    - location_match_score: Location alignment
    - final_weighted_score: Weighted combination of all factors
    - match_percentage: Final score as percentage
    """
    try:
        # Calculate individual scores
        cosine_sim = cosine_similarity(job_embedding, candidate_embedding)
        
        # Normalize cosine similarity to 0-1 range (from -1 to 1)
        cosine_norm = (cosine_sim + 1) / 2
        
        skill_score = calculate_skill_match_score(job_skills or [], candidate_skills or [])
        exp_score = calculate_experience_match_score(job_exp_required, candidate_exp or 0)
        edu_score = calculate_education_match_score(job_qualifications, candidate_degree or "", candidate_cgpa)
        loc_score = calculate_location_match_score(job_location, candidate_location)
        
        # Calculate weighted final score
        weights = MATCHING_WEIGHTS
        weighted_score = (
            cosine_norm * weights['embeddings_similarity'] +
            skill_score * weights['skills_match'] +
            exp_score * weights['experience_match'] +
            edu_score * weights['education_match'] +
            loc_score * weights['location_match']
        )
        
        # Convert to percentage
        match_percentage = round(weighted_score * 100, 2)
        
        return {
            'cosine_similarity_score': round(cosine_sim, 4),
            'skill_match_score': round(skill_score, 4),
            'experience_match_score': round(exp_score, 4),
            'education_match_score': round(edu_score, 4),
            'location_match_score': round(loc_score, 4),
            'final_weighted_score': round(weighted_score, 4),
            'match_percentage': match_percentage
        }
        
    except Exception as e:
        logger.error(f"Composite match score calculation failed: {str(e)}")
        raise

# ============================================================================
# BATCH MATCHING
# ============================================================================
def find_top_k_matches(
    job_embedding: List[float],
    candidates: List[Dict[str, Any]],
    job_data: Dict[str, Any],
    k: int = 10,
    min_threshold: float = MIN_SIMILARITY_THRESHOLD
) -> List[Dict[str, Any]]:
    """
    Find top K matching candidates for a job
    Args:
        job_embedding: Embedding vector of the job
        candidates: List of candidate data dictionaries
        job_data: Job posting details
        k: Number of top matches to return
        min_threshold: Minimum score threshold for matches
    Returns: Sorted list of top matches with scores
    """
    try:
        matches = []
        
        for candidate in candidates:
            if not candidate.get('profile_embedding'):
                continue
            
            # Calculate composite scores
            scores = calculate_composite_match_score(
                job_embedding,
                candidate['profile_embedding'],
                job_skills=job_data.get('skills_required', []),
                candidate_skills=candidate.get('skills', []),
                job_exp_required=job_data.get('experience_required_years', 0),
                candidate_exp=candidate.get('years_of_experience', 0),
                job_qualifications=job_data.get('required_qualifications', ""),
                candidate_degree=candidate.get('education_degree', ""),
                candidate_cgpa=candidate.get('current_cgpa'),
                job_location=job_data.get('location', ""),
                candidate_location=candidate.get('current_location', "")
            )
            
            # Only include if meets threshold
            if scores['final_weighted_score'] >= min_threshold:
                match = {
                    'candidate_id': candidate.get('candidate_id'),
                    'candidate_name': candidate.get('candidate_name'),
                    'email_address': candidate.get('email_address'),
                    **scores
                }
                matches.append(match)
        
        # Sort by weighted score descending
        matches.sort(key=lambda x: x['final_weighted_score'], reverse=True)
        
        return matches[:k]
        
    except Exception as e:
        logger.error(f"Top K matches finding failed: {str(e)}")
        raise
