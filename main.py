import os
import uvicorn
from routers import profileparser
from routers import vector
from routers import vector_storage
from routers import candidate_matching
from fastapi import FastAPI

app = FastAPI(title="Resume AI API", description="API for parsing resumes and profiles")

# This "mounts" all the routes from that file into your main app
app.include_router(profileparser.router)
app.include_router(vector.router)
app.include_router(vector_storage.router)
app.include_router(candidate_matching.router)

@app.get("/")
def home():
    return {"message": "API is running. Go to /docs for the playground."}

if __name__ == "__main__":
    # Cloud Run provides the 'PORT' env var. 
    # If it's missing (local dev), we default to 8080.
    port = int(os.environ.get("PORT", 8080))
    
    # CRITICAL: You must use host="0.0.0.0" 
    uvicorn.run(app, host="127.0.0.1", port=port)
    #uvicorn.run(app, host="0.0.0.0", port=8000)