# Local Development Setup (Before Committing to Git)

If you want to test the application locally **before committing to Git**, follow these steps.

---

## ⚠️ Important Note

**This is optional**: You don't need to test locally if you're confident the code is working. You can commit directly to git and your GitHub Actions workflow will build and deploy to Cloud Run.

But if you want to verify locally first, follow this guide.

---

## 🚀 Quick Local Test (5 minutes)

### Prerequisites
- Python 3.9+ installed
- PostgreSQL 12+ installed and running locally
- Google Gemini API key from https://aistudio.google.com

### 1. Navigate to Project

```bash
cd "d:\ABHRA\INTERNSHIPS\CampusHire - March 2026\Codebase\search-engine-main"
```

### 2. Create Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create Local .env File

```bash
# Create .env for local testing (this will NOT be committed to git)
(New-Item -Path ".env" -ItemType File -Force) | Out-Null

# Add this content to .env:
@"
DB_HOST=localhost
DB_PORT=5432
DB_NAME=campushire_db
DB_USER=postgres
DB_PASSWORD=postgres
GEMINI_API_KEY=your_gemini_api_key_here
MY_API_AUTH_KEY=test_dev_key_12345
MIN_SIMILARITY_THRESHOLD=0.4
DEFAULT_TOP_K=10
"@ | Set-Content .env
```

### 5. Setup Database

```bash
# Create the database in PostgreSQL
psql -U postgres -c "CREATE DATABASE campushire_db;"

# Verify connection
psql -U postgres -d campushire_db -c "SELECT 1;"
```

### 6. Run Application

```bash
python main.py
```

Expected output:
```
INFO:     Started server process
INFO:     Uvicorn running on http://127.0.0.1:8080
```

### 7. Test in Browser

Visit: http://localhost:8080/docs

You should see the Swagger UI with all 15+ endpoints!

---

## 🧪 Quick Test Endpoints

### Test 1: Health Check (30 seconds)

```bash
curl -X GET "http://localhost:8080/health"
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-04-13T...",
  "service": "CampusHire",
  "version": "1.0.0"
}
```

### Test 2: Create Job (2 minutes)

```bash
curl -X POST "http://localhost:8080/api/v1/recruiter/jobs/create" \
  -H "X-API-Key: test_dev_key_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "recruiter_id": "recruiter_1",
    "job_title": "Python Developer",
    "job_description": "5+ years Python, FastAPI, PostgreSQL",
    "skills_required": ["Python", "FastAPI", "PostgreSQL"],
    "experience_required_years": 5,
    "location": "bangalore",
    "employment_type": "full-time",
    "required_qualifications": "B.Tech"
  }'
```

Expected response:
```json
{
  "status": "success",
  "job_id": 1,
  "message": "Job posting created successfully"
}
```

### Test 3: Create Candidate (2 minutes)

```bash
curl -X POST "http://localhost:8080/api/v1/candidate/profile/create" \
  -H "X-API-Key: test_dev_key_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_name": "John Doe",
    "email_address": "john@example.com",
    "current_location": "bangalore",
    "skills": ["Python", "FastAPI", "PostgreSQL"],
    "years_of_experience": 5,
    "education_degree": "B.Tech",
    "education_institute": "IIT",
    "current_cgpa": 8.0
  }'
```

---

## 🐛 Troubleshooting Local Tests

### Error: "Database connection failed"

```bash
# Check PostgreSQL is running
psql --version

# Or start PostgreSQL service
# (Windows) sc start postgresql-x64-12
```

### Error: "Module not found"

```bash
# Make sure venv is activated
venv\Scripts\activate

# Reinstall requirements
pip install -r requirements.txt
```

### Error: "API Key Invalid"

```bash
# Check .env file has correct key
type .env

# Or set it directly
$env:MY_API_AUTH_KEY="test_dev_key_12345"
```

---

## 📝 Testing Tips

1. **Use Swagger UI**: Go to http://localhost:8080/docs - much easier than curl!
2. **Check logs**: Watch the terminal for detailed error messages
3. **Test order**: Always test health → create resources → embed → match
4. **Save IDs**: Save job_id and candidate_id from responses for next tests

---

## ✅ After Successful Local Test

If everything works locally:

```bash
# Stop the server (Ctrl+C)

# Deactivate venv (optional)
deactivate

# Remove local .env (it's in .gitignore anyway)
del .env

# Commit to git
git add .
git commit -m "Initial commit: CampusHire full implementation"
git push origin main
```

GitHub Actions will then automatically:
1. Build Docker image
2. Push to Artifact Registry
3. Deploy to Cloud Run

---

## ⏭️ What Happens After Commit

1. **GitHub Actions triggers** - See .github/workflows/deploy.yml
2. **Docker image built** - In Artifact Registry
3. **Deployed to Cloud Run** - Service updated
4. **Secrets injected** - From Secret Manager
5. **API live** - At https://search-engine-api-...asia-south1.a.run.app

---

## 📚 Full Documentation

For detailed information:
- **Local setup:** [QUICKSTART.md](QUICKSTART.md)
- **Production:** [CLOUD_RUN_SETUP.md](CLOUD_RUN_SETUP.md)
- **Testing:** [API_TESTING.md](API_TESTING.md)
- **Configuration:** [CONFIGURATION.md](CONFIGURATION.md)

---

## 🎯 Summary

**To commit without testing:**
```bash
git add .
git commit -m "Initial commit: CampusHire implementation"
git push origin main
```

**To test locally first:**
```bash
# Follow steps 1-7 above
# Then commit when everything works
```

---

**Either way, you're ready! 🎉**

The project is clean, documented, and production-ready!
