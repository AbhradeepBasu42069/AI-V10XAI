import os
import json
from google import genai
from dotenv import load_dotenv
from google.genai import types
#from google.api_core import exceptions
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel  # For request validation
from auth import validate_api_key
from .vector_storage import store_vector_embedding, VectorStorageRequest
# Load environment variables
load_dotenv()

router = APIRouter(prefix="/vector", 
    tags=["vector Operations"],
    dependencies=[Depends(validate_api_key)])

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
class VectorRequest(BaseModel):
    profile_id: int
    json_profile: dict
    
def json_to_markdown(data):
    """Converts flat JSON into a clean Markdown string."""
    lines = ["# Candidate Profile"]
    for key, value in data.items():
        # Clean up the key (e.g., 'years_exp' -> 'Years Exp')
        clean_key = key.replace('_', ' ').title()
        lines.append(f"- **{clean_key}**: {value}")
    
    return "\n".join(lines)

# Example Output:
# # Candidate Profile
# - **Full Name**: Michael Staffer
# - **Top Skill**: Machine Learning
def process_and_embed(json_profile):
    # 1. Convert to Markdown (saves tokens + improves context)
    formatted_text = json_to_markdown(json_profile)
    print(formatted_text)
    # 2. Get the 768-D vector
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=formatted_text,
        config={'output_dimensionality': 768}
    )
    
    return response.embeddings[0].values

# Now your vector is based on a human-readable profile, not raw JSON code.

@router.post("/vectorconversion")
def json_to_vector_conversion(request: VectorRequest):
    profile_json = request.json_profile
    profile_id = request.profile_id
    try:
        #convert to vector
        profile_vector = process_and_embed(profile_json)
        
        # Store the vector
        storage_request = VectorStorageRequest(
            profile_id=profile_id,
            embedding=profile_vector,
            metadata=profile_json
        )
        store_vector_embedding(storage_request)

        return {"profile_id": profile_id, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
