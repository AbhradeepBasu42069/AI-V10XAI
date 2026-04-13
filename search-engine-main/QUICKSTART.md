# CampusHire Quick Start Guide

Get the CampusHire system running in 10 minutes!

## 📋 Prerequisites

- Python 3.9+ installed
- PostgreSQL 12+ installed and running
- Google Gemini API key from [https://aistudio.google.com](https://aistudio.google.com)
- Git installed

---

## 🚀 Quick Setup (5 minutes)

### 1. Clone Repository

```bash
git clone <repository-url>
cd search-engine-main
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Database

```bash
# Create database
psql -U postgres -c "CREATE DATABASE campushire_db;"

# Verify connection (optional)
psql -U postgres -d campushire_db -c "SELECT 1;"
```

### 5. Configure Environment

```bash
# Copy example file
cp .env.example .env

# Edit .env - Add your credentials:
# DB_PASSWORD=your_postgres_password
# GEMINI_API_KEY=your_gemini_api_key_from_google
# MY_API_AUTH_KEY=create_a_strong_secret_key
```

**Sample .env:**
```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=campushire_db
DB_USER=postgres
DB_PASSWORD=postgres123
GEMINI_API_KEY=AIzaSyD...your_key...
MY_API_AUTH_KEY=sk_dev_campushire_2024_secret
MIN_SIMILARITY_THRESHOLD=0.4
DEFAULT_TOP_K=10
```

### 6. Run Application

```bash
python main.py
```

**Output:**
```
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://127.0.0.1:8080
INFO:     Press CTRL+C to quit
```

---

## 🔗 API Access

### Open in Browser
- **Swagger Docs**: [http://localhost:8080/docs](http://localhost:8080/docs)
- **ReDoc Docs**: [http://localhost:8080/redoc](http://localhost:8080/redoc)
- **Health Check**: [http://localhost:8080/health](http://localhost:8080/health)

### Get API Key Ready

Use this key in all requests:
```
X-API-Key: sk_dev_campushire_2024_secret
```

---

## 🧪 Quick Test Flows

### Test 1: Create & Match Job (5 minutes)

**Step 1: Create Job Posting**
```bash
curl -X POST "http://localhost:8080/api/v1/recruiter/jobs/create" \
  -H "X-API-Key: sk_dev_campushire_2024_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "recruiter_id": "test_recruiter_1",
    "job_title": "Python Developer",
    "job_description": "Looking for a Python developer with FastAPI experience",
    "skills_required": ["Python", "FastAPI", "PostgreSQL", "Docker"],
    "experience_required_years": 3,
    "location": "bangalore",
    "employment_type": "full-time",
    "required_qualifications": "B.Tech or equivalent"
  }'
```

**Response contains:** `job_id` (save this!)

**Step 2: Generate Job Embedding**
```bash
curl -X POST "http://localhost:8080/api/v1/recruiter/jobs/embed" \
  -H "X-API-Key: sk_dev_campushire_2024_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 1
  }'
```

**Response:** Confirms embedding generated

### Test 2: Create & Embed Candidate (5 minutes)

**Step 1: Parse Resume**
```bash
curl -X POST "http://localhost:8080/api/v1/candidate/profile/parse" \
  -H "X-API-Key: sk_dev_campushire_2024_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "John Doe\nEmail: john@test.com\nPython Developer\n5 years experience\nSkills: Python, FastAPI, PostgreSQL, Docker, AWS"
  }'
```

**Step 2: Create Candidate**
```bash
curl -X POST "http://localhost:8080/api/v1/candidate/profile/create" \
  -H "X-API-Key: sk_dev_campushire_2024_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_name": "John Doe",
    "email_address": "john@test.com",
    "current_location": "bangalore",
    "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
    "years_of_experience": 5,
    "education_degree": "B.Tech",
    "education_institute": "IIT",
    "current_cgpa": 8.0
  }'
```

**Save:** `candidate_id` from response

**Step 3: Generate Candidate Embedding**
```bash
curl -X POST "http://localhost:8080/api/v1/candidate/profile/embed" \
  -H "X-API-Key: sk_dev_campushire_2024_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": 1
  }'
```

### Test 3: Find Matches (1 minute)

**Find Candidates for Job:**
```bash
curl -X POST "http://localhost:8080/api/v1/match/find-candidates" \
  -H "X-API-Key: sk_dev_campushire_2024_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 1,
    "top_k": 10,
    "min_threshold": 0.4
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "job_id": 1,
  "matches_found": 1,
  "matches": [
    {
      "candidate_id": 1,
      "candidate_name": "John Doe",
      "scores": {
        "final_weighted_score": 0.92,
        "match_percentage": 92.0
      }
    }
  ]
}
```

---

## 📊 Common Endpoints Reference

| Operation | Endpoint | Method |
|-----------|----------|--------|
| Create Job | `/api/v1/recruiter/jobs/create` | POST |
| Embed Job | `/api/v1/recruiter/jobs/embed` | POST |
| Get Job | `/api/v1/recruiter/jobs/{id}` | GET |
| List Jobs | `/api/v1/recruiter/jobs` | GET |
| Parse Resume | `/api/v1/candidate/profile/parse` | POST |
| Create Candidate | `/api/v1/candidate/profile/create` | POST |
| Embed Candidate | `/api/v1/candidate/profile/embed` | POST |
| Get Candidate | `/api/v1/candidate/profile/{id}` | GET |
| Find Candidates | `/api/v1/match/find-candidates` | POST |
| Find Jobs | `/api/v1/match/find-jobs` | POST |

---

## 🐛 Troubleshooting

### Issue: Database Connection Failed

```
psycopg2.OperationalError: could not connect to server
```

**Solution:**
1. Ensure PostgreSQL is running: `psql --version`
2. Verify credentials in `.env`
3. Check if `campushire_db` exists: `psql -U postgres -l`

### Issue: GEMINI_API_KEY Error

```
google.auth.exceptions.DefaultCredentialsError
```

**Solution:**
1. Get key from [https://aistudio.google.com](https://aistudio.google.com)
2. Copy exact key to `.env`
3. Reload environment: Restart application

### Issue: 401 Unauthorized

```
Invalid or missing API Key
```

**Solution:**
1. Add `X-API-Key` header to requests
2. Match key in `.env` file

### Issue: No Embeddings Found

```
error: "Job must have embedding"
```

**Solution:**
1. Create job first: POST `/recruiter/jobs/create`
2. Generate embedding: POST `/recruiter/jobs/embed` with job_id
3. Wait for completion before matching

---

## 📚 Next Steps

1. **Read Full Documentation**: See `README_COMPLETE.md`
2. **Understand Algorithm**: See `SYSTEM_FLOW.md`
3. **Explore API Docs**: Visit `/docs` in browser
4. **Copy to Production**: See deployment guide in README

---

## 💡 Tips

- **Save IDs**: Always save `job_id` and `candidate_id` for later use
- **Use Browser**: Open `/docs` to test APIs in Swagger UI
- **Check Logs**: Watch terminal for request logs
- **Set Headers**: Always include `X-API-Key` header
- **Parse First**: Always parse resume before creating candidate profile

---

## ✅ You're Ready!

The system is now running. Start by:
1. Creating a job posting
2. Creating a candidate
3. Finding matches!

For questions, check `README_COMPLETE.md` or `SYSTEM_FLOW.md`.

---

**Need Help?**
- Check `.env` configuration
- Verify PostgreSQL is running
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Review error messages in terminal
