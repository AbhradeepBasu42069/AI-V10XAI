import os
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv

# Define the header name the client must send
load_dotenv()   
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
#print(api_key_header)
# Get your custom secret from environment variables
MY_API_AUTH_KEY = os.getenv("MY_API_AUTH_KEY", "fallback_dev_key")

def validate_api_key(api_key: str = Security(api_key_header)):
    if api_key == MY_API_AUTH_KEY:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",

    )
