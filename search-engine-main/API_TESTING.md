# CampusHire API Testing Guide

Complete collection of curl commands and examples to test all API endpoints.

---

## 🔧 Setup

Before testing, ensure:
1. Application running: `python main.py`
2. API key ready: `sk_dev_campushire_2024_secret` (or your configured key)
3. Database accessible

---

## 📊 Recruiter Job Endpoints

### 1. Get Health Check

```bash
curl -X GET "http://localhost:8080/api/v1/recruiter/health" \
  -H "X-API-Key: sk_dev_campushire_2024_secret"
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "recruiter-jobs",
  "total_active_jobs": 0
}
```

---

### 2. Create Job Posting

```bash
curl -X POST "http://localhost:8080/api/v1/recruiter/jobs/create" \
  -H "X-API-Key: sk_dev_campushire_2024_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "recruiter_id": "recruiter_001",
    "job_title": "Senior Python Developer",
    "job_description": "We are seeking a Senior Python Developer with expertise in building scalable backend systems using modern technologies like FastAPI, Django, and microservices architecture. You will work on critical infrastructure serving millions of users.",
    "skills_required": [
      "Python",
      "FastAPI",
      "PostgreSQL",
      "Docker",
      "Kubernetes",
      "AWS",
      "Redis"
    ],
    "experience_required_years": 5,
    "salary_range_min": 1200000,
    "salary_range_max": 2000000,
    "location": "Bangalore",
    "employment_type": "full-time",
    "industry": "Technology",
    "job_category": "Backend Development",
    "required_qualifications": "B.Tech in Computer Science or 5+ years of professional development experience"
  }'
```

**Capture:** `job_id` from response (e.g., 42)

---

### 3. Generate Job Embedding

```bash
curl -X POST "http://localhost:8080/api/v1/recruiter/jobs/embed" \
  -H "X-API-Key: sk_dev_campushire_2024_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 42
  }'
```

---

### 4. Get Job Details

```bash
curl -X GET "http://localhost:8080/api/v1/recruiter/jobs/42" \
  -H "X-API-Key: sk_dev_campushire_2024_secret"
```

---

### 5. List All Recruiter Jobs

```bash
curl -X GET "http://localhost:8080/api/v1/recruiter/jobs?recruiter_id=recruiter_001&limit=20&offset=0" \
  -H "X-API-Key: sk_dev_campushire_2024_secret"
```

---

### 6. Update Job Status

```bash
# Deactivate job
curl -X PUT "http://localhost:8080/api/v1/recruiter/jobs/42/status?status=inactive" \
  -H "X-API-Key: sk_dev_campushire_2024_secret"

# Reactivate job
curl -X PUT "http://localhost:8080/api/v1/recruiter/jobs/42/status?status=active" \
  -H "X-API-Key: sk_dev_campushire_2024_secret"
```

---

## 👥 Candidate Endpoints

### 1. Get Health Check

```bash
curl -X GET "http://localhost:8080/api/v1/candidate/health" \
  -H "X-API-Key: sk_dev_campushire_2024_secret"
```

---

### 2. Parse Resume

```bash
curl -X POST "http://localhost:8080/api/v1/candidate/profile/parse" \
  -H "X-API-Key: sk_dev_campushire_2024_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "JOHN DOE\nEmail: john.doe@email.com\nPhone: +91-9876543210\nLocation: Bangalore, India\n\nOBJECTIVE:\nSeeking a challenging position as Senior Developer to leverage my 6 years of experience in backend development.\n\nEDUCATION:\nB.Tech in Computer Science\nIndian Institute of Technology Bombay\nGPA: 8.5/10\nGraduation: 2018\n\nPROFESSIONAL EXPERIENCE:\nSenior Backend Developer\nTechCorp Solutions (2020 - Present)\nDeveloped scalable REST APIs using FastAPI\nManaged PostgreSQL databases with 1M+ records\nDeployed applications using Docker and Kubernetes\nLed a team of 2 junior developers\nExperience: 4 years\nCTC: 1.5 LPA\n\nBackend Developer\nStartupXYZ (2018 - 2020)\nBuilt authentication systems using Python\nOptimized database queries reducing response time by 40%\nExperience: 2 years\n\nSKILLS:\nProgramming: Python, JavaScript, Java\nFrameworks: FastAPI, Django, Flask\nDatabases: PostgreSQL, MongoDB, Redis\nDevOps: Docker, Kubernetes, AWS (EC2, S3, RDS)\nTools: Git, JIRA, Linux, VS Code\n\nPROJECTS:\n1. E-commerce Platform\n   Built scalable backend using FastAPI\n   Implemented payment integration with Stripe\n   Used PostgreSQL with Redis caching\n   Tech: Python, FastAPI, PostgreSQL, Redis\n\n2. Real-time Chat Application\n   Built WebSocket-based chat system\n   Deployed on AWS using ECS\n   Tech: Python, WebSockets, AWS\n\nCERTIFICATIONS:\n- AWS Solutions Architect Associate (2023)\n- Docker Certified Associate (2022)\n- AWS Developer Associate (2023)\n\nPUBLIC PROFILES:\nGitHub: github.com/johndoe\nLinkedIn: linkedin.com/in/johndoe\nPortfolio: johndoe.dev\n\nWORK PREFERENCES:\nPreferred Roles: Senior Developer, Tech Lead, Architect\nEmployment Type: Full-time\nNotice Period: 30 days\nWork Authorization: Indian National"
  }'
```

**Response contains:** Parsed resume JSON. Save this for reference.

---

### 3. Create Candidate Profile

Using the parsed resume data:

```bash
curl -X POST "http://localhost:8080/api/v1/candidate/profile/create" \
  -H "X-API-Key: sk_dev_campushire_2024_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_name": "John Doe",
    "email_address": "john.doe@email.com",
    "phone_number": "+91-9876543210",
    "current_location": "Bangalore",
    "skills": [
      "Python",
      "JavaScript",
      "Java",
      "FastAPI",
      "Django",
      "Flask",
      "PostgreSQL",
      "MongoDB",
      "Redis",
      "Docker",
      "Kubernetes",
      "AWS",
      "Git"
    ],
    "years_of_experience": 6,
    "current_cgpa": 8.5,
    "latest_company": "TechCorp Solutions",
    "latest_role_title": "Senior Backend Developer",
    "education_degree": "B.Tech",
    "education_institute": "Indian Institute of Technology Bombay",
    "education_branch": "Computer Science",
    "notice_period_days": 30,
    "work_authorization": "Indian National",
    "preferred_roles": ["Senior Developer", "Tech Lead", "Architect"],
    "employment_type_preference": "full-time"
  }'
```

**Capture:** `candidate_id` from response (e.g., 78)

---

### 4. Generate Candidate Embedding

```bash
curl -X POST "http://localhost:8080/api/v1/candidate/profile/embed" \
  -H "X-API-Key: sk_dev_campushire_2024_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": 78
  }'
```

---

### 5. Get Candidate Profile

```bash
curl -X GET "http://localhost:8080/api/v1/candidate/profile/78" \
  -H "X-API-Key: sk_dev_campushire_2024_secret"
```

---

### 6. List All Candidates

```bash
# List all candidates
curl -X GET "http://localhost:8080/api/v1/candidate/profiles?limit=20&offset=0" \
  -H "X-API-Key: sk_dev_campushire_2024_secret"

# Filter by location
curl -X GET "http://localhost:8080/api/v1/candidate/profiles?location=bangalore&limit=20" \
  -H "X-API-Key: sk_dev_campushire_2024_secret"
```

---

### 7. Update Candidate Status

```bash
# Deactivate candidate
curl -X PUT "http://localhost:8080/api/v1/candidate/profile/78/status?status=inactive" \
  -H "X-API-Key: sk_dev_campushire_2024_secret"

# Mark as hired
curl -X PUT "http://localhost:8080/api/v1/candidate/profile/78/status?status=hired" \
  -H "X-API-Key: sk_dev_campushire_2024_secret"
```

---

## 🎯 Matching Endpoints

### 1. Get Health Check

```bash
curl -X GET "http://localhost:8080/api/v1/match/health" \
  -H "X-API-Key: sk_dev_campushire_2024_secret"
```

---

### 2. Find Candidates for Job

This is the main matching endpoint for recruiters:

```bash
curl -X POST "http://localhost:8080/api/v1/match/find-candidates" \
  -H "X-API-Key: sk_dev_campushire_2024_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 42,
    "top_k": 10,
    "min_threshold": 0.4
  }'
```

**Response includes:**
- List of matching candidates
- Individual scores for each factor
- Final weighted score
- Match percentage

---

### 3. Find Jobs for Candidate

This is the main matching endpoint for candidates:

```bash
curl -X POST "http://localhost:8080/api/v1/match/find-jobs" \
  -H "X-API-Key: sk_dev_campushire_2024_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": 78,
    "top_k": 10
  }'
```

---

### 4. Get Job Match Results

Retrieve stored matches for a job:

```bash
curl -X GET "http://localhost:8080/api/v1/match/job/42/results?limit=50" \
  -H "X-API-Key: sk_dev_campushire_2024_secret"
```

---

### 5. Get Candidate Match Results

Retrieve stored matches for a candidate:

```bash
curl -X GET "http://localhost:8080/api/v1/match/candidate/78/results?limit=50" \
  -H "X-API-Key: sk_dev_campushire_2024_secret"
```

---

## 🔍 System Health Endpoints

### 1. Application Health

```bash
curl -X GET "http://localhost:8080/health" \
  -H "X-API-Key: sk_dev_campushire_2024_secret"
```

---

### 2. Version Info

```bash
curl -X GET "http://localhost:8080/version" \
  -H "X-API-Key: sk_dev_campushire_2024_secret"
```

---

## 📋 Full Test Scenario

Run these commands in order to test the complete workflow:

### Step 1: Create Job (Record job_id)
```bash
JOB_RESPONSE=$(curl -s -X POST "http://localhost:8080/api/v1/recruiter/jobs/create" \
  -H "X-API-Key: sk_dev_campushire_2024_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "recruiter_id": "test_recruiter",
    "job_title": "Python Developer",
    "job_description": "We need a Python developer with FastAPI experience",
    "skills_required": ["Python", "FastAPI", "PostgreSQL"],
    "experience_required_years": 3,
    "location": "bangalore",
    "employment_type": "full-time",
    "required_qualifications": "B.Tech"
  }')

echo "$JOB_RESPONSE" | grep -o '"job_id":[^,]*'
```

### Step 2: Embed Job
Replace `{job_id}` with the ID from Step 1:
```bash
curl -X POST "http://localhost:8080/api/v1/recruiter/jobs/embed" \
  -H "X-API-Key: sk_dev_campushire_2024_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 1
  }'
```

### Step 3: Create Candidate (Record candidate_id)
```bash
CANDIDATE_RESPONSE=$(curl -s -X POST "http://localhost:8080/api/v1/candidate/profile/create" \
  -H "X-API-Key: sk_dev_campushire_2024_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_name": "Test Candidate",
    "email_address": "test@example.com",
    "current_location": "bangalore",
    "skills": ["Python", "FastAPI", "PostgreSQL"],
    "years_of_experience": 4,
    "education_degree": "B.Tech",
    "education_institute": "IIT",
    "current_cgpa": 8.0
  }')

echo "$CANDIDATE_RESPONSE" | grep -o '"candidate_id":[^,]*'
```

### Step 4: Embed Candidate
```bash
curl -X POST "http://localhost:8080/api/v1/candidate/profile/embed" \
  -H "X-API-Key: sk_dev_campushire_2024_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": 1
  }'
```

### Step 5: Find Matches
```bash
curl -X POST "http://localhost:8080/api/v1/match/find-candidates" \
  -H "X-API-Key: sk_dev_campushire_2024_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 1,
    "top_k": 10
  }'
```

Expected result: Candidate should appear with high match score (80%+)

---

## 🛠️ Debugging Tips

### Check Database Connection
```bash
psql -U postgres -d campushire_db -c "SELECT COUNT(*) FROM recruiter_jobs;"
```

### View Logs in Terminal
Application prints detailed logs showing:
- Database operations
- Embedding generation
- Matching calculations
- API requests/responses

### Test Without API Key
To verify API key protection:
```bash
curl -X GET "http://localhost:8080/api/v1/recruiter/health"
# Should return: Invalid or missing API Key
```

### Check Response Format
All responses follow this format:
```json
{
  "status": "success|error",
  "data": {...},
  "message": "...",
  "timestamp": "2024-01-15T10:30:45"
}
```

---

## 📊 Testing Checklist

- [ ] Job creation works
- [ ] Job embedding generation works
- [ ] Candidate profile creation works
- [ ] Candidate embedding generation works
- [ ] Matching algorithm runs
- [ ] Results are stored in database
- [ ] Match history retrieval works
- [ ] Health checks pass
- [ ] Error handling works
- [ ] API key validation works

---

## 💾 Database Verification Queries

```sql
-- Check jobs created
SELECT COUNT(*) as total_jobs FROM recruiter_jobs;

-- Check candidates created
SELECT COUNT(*) as total_candidates FROM candidate_profiles;

-- Check matches stored
SELECT COUNT(*) as total_matches FROM matching_results;

-- View top matches
SELECT m.*, c.candidate_name, j.job_title
FROM matching_results m
JOIN candidate_profiles c ON m.candidate_id = c.candidate_id
JOIN recruiter_jobs j ON m.job_id = j.job_id
ORDER BY m.final_weighted_score DESC
LIMIT 10;
```

---

## 🎯 Common Test Cases

### Test Case 1: Perfect Match
- Create job requiring: Python, FastAPI, PostgreSQL, 5 years
- Create candidate with: Python, FastAPI, PostgreSQL, 6 years
- Expected: 85%+ match score

### Test Case 2: Partial Match
- Create job requiring: Python, Java, Go, 5 years
- Create candidate with: Python, JavaScript, 3 years
- Expected: 40-60% match score

### Test Case 3: No Match
- Create job requiring: Go, Rust, 10 years
- Create candidate with: Python, JavaScript, 2 years
- Expected: <40% (filtered out by threshold)

---

## ✅ Success Criteria

A successful test should show:
1. ✓ All CRUD operations work
2. ✓ Embeddings generated successfully
3. ✓ Matching algorithm produces scores 0-100%
4. ✓ Results stored in database
5. ✓ API responses contain all expected fields
6. ✓ Error handling works correctly
7. ✓ Performance acceptable (<10 seconds for matching)

---

**Ready to test?** Start with the Quick Test Flows above!
