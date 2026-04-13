import os
import json
import time
#import google.generativeai as genai
from google import genai    
from google.genai import types
#from google.api_core import exceptions
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel  # For request validation
from dotenv import load_dotenv
from auth import validate_api_key

# Load environment variables
load_dotenv()

router = APIRouter(prefix="/profile", 
    tags=["Profile Parser Operations"],
    dependencies=[Depends(validate_api_key)])

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class ProfileRequest(BaseModel):
    profile_text: str

@router.get("/health")
def health_check():
    return {"status": "online", "method": "parse"}

@router.post("/parse")
def parse_profile_to_json(request: ProfileRequest):
    profile_text = request.profile_text
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

    # Create the prompt
    prompt = f"""
    You are a precise data extraction assistant. 
    Analyze the following resume text and extract the data to match the EXACT JSON structure provided below.
    
    Rules:
    1. If a field is not found in the text, return null or an empty string.
    2. Do not invent information.
    3. Output must be valid JSON only.
    
    Target JSON Structure:
    {json.dumps(desired_structure, indent=2)}
    
    Profile Text:
    {profile_text} 
    """

    try:
        #response = model.generate_content(prompt)
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type='application/json'
            )
        )
        #print(response.text)
        return json.loads(response.text)
    except Exception as e:
        #print(e)
        raise HTTPException(status_code=500, detail=str(e))
        #return {"error": f"AI Parsing failed: {e}"}

