# CampusHire: Recruiter-Candidate Matching System

## 📋 Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [System Components](#system-components)
4. [Database Schema](#database-schema)
5. [Matching Algorithm](#matching-algorithm)
6. [Installation](#installation)
7. [Configuration](#configuration)
8. [API Documentation](#api-documentation)
9. [Complete Workflow](#complete-workflow)
10. [Development](#development)
11. [Deployment](#deployment)

---

## 🎯 Overview

**CampusHire** is an AI-powered recruiter-to-candidate matching system that uses semantic embeddings and advanced matching algorithms to connect job seekers with relevant opportunities.

### Key Features
- **AI-Powered Matching**: Uses Google's Gemini API for semantic embeddings
- **Multi-Factor Scoring**: Combines multiple matching criteria (skills, experience, education, location)
- **Resume Parsing**: Automatic resume parsing and data extraction
- **PostgreSQL Storage**: Persistent storage of embeddings and match history
- **RESTful API**: Complete REST API with comprehensive documentation
- **Scalable Architecture**: Optimized database queries with indexing

### Technology Stack
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL with JSONB support
- **AI Engine**: Google Gemini API for embeddings
- **Vector Operations**: NumPy
- **Deployment**: Docker, Cloud Run compatible

---

## 🏗️ Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT APPLICATIONS                       │
│  (Web Portal, Mobile App, Recruiter Dashboard)              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  FASTAPI APPLICATION LAYER                   │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Recruiter   │  │  Candidate   │  │   Matching  │      │
│  │   Routes    │  │    Routes    │  │    Routes   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                  ┌───────────┴───────────┐
                  ▼                       ▼
        ┌──────────────────┐    ┌──────────────────┐
        │ Embedding Utils  │    │  Database Mgmt   │
        │  (Google Gemini) │    │   (PostgreSQL)   │
        └──────────────────┘    └──────────────────┘
                  │                       │
                  ▼                       ▼
        ┌──────────────────┐    ┌──────────────────┐
        │  Google Gemini   │    │   PostgreSQL     │
        │  Embedding API   │    │   Database       │
        └──────────────────┘    └──────────────────┘
```

### Data Flow

```
1. RECRUITER FLOW
   Create Job → Parse Job Description → Generate Job Embedding → Store in DB

2. CANDIDATE FLOW
   Upload Resume → Parse Resume → Extract Data → Generate Embedding → Store in DB

3. MATCHING FLOW
   Request Matches → Calculate Scores → Sort by Relevance → Return Results → Store History

4. RETRIEVAL FLOW
   Query by Job/Candidate → Retrieve from DB → Return Historical Matches
```

---

## 🔧 System Components

### 1. **Recruiter Module** (`routers/recruiter.py`)
Handles job posting management and recruiter operations.

**Endpoints:**
- `POST /api/v1/recruiter/jobs/create` - Create new job posting
- `POST /api/v1/recruiter/jobs/embed` - Generate job embedding
- `GET /api/v1/recruiter/jobs/{job_id}` - Retrieve job details
- `GET /api/v1/recruiter/jobs` - List recruiter's jobs
- `PUT /api/v1/recruiter/jobs/{job_id}/status` - Update job status

### 2. **Candidate Module** (`routers/candidate.py`)
Handles candidate profile and resume parsing.

**Endpoints:**
- `POST /api/v1/candidate/profile/parse` - Parse resume text
- `POST /api/v1/candidate/profile/create` - Create candidate profile
- `POST /api/v1/candidate/profile/embed` - Generate candidate embedding
- `GET /api/v1/candidate/profile/{candidate_id}` - Get candidate details
- `GET /api/v1/candidate/profiles` - List candidates

### 3. **Matching Module** (`routers/matching.py`)
Handles AI-powered matching between jobs and candidates.

**Endpoints:**
- `POST /api/v1/match/find-candidates` - Find candidates for a job
- `POST /api/v1/match/find-jobs` - Find jobs for a candidate
- `GET /api/v1/match/job/{job_id}/results` - Get job match history
- `GET /api/v1/match/candidate/{candidate_id}/results` - Get candidate match history

### 4. **Database Module** (`database.py`)
Manages all database operations and schema.

**Responsibilities:**
- Database connection management
- Schema initialization
- CRUD operations for jobs, candidates, and matches
- Query optimization with indexes

### 5. **Embedding Module** (`embedding_utils.py`)
Handles embedding generation and similarity calculations.

**Key Functions:**
- `generate_embedding()` - Generate embedding using Gemini API
- `cosine_similarity()` - Calculate similarity between vectors
- `calculate_composite_match_score()` - Multi-factor matching

### 6. **Configuration** (`config.py`)
Centralized configuration management.

**Contains:**
- Database credentials
- API keys
- Matching weights and thresholds
- Model parameters

---

## 📊 Database Schema

### Table 1: `recruiter_jobs`
Stores job postings from recruiters.

```sql
CREATE TABLE recruiter_jobs (
    job_id SERIAL PRIMARY KEY,
    recruiter_id VARCHAR(255) NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    job_description TEXT NOT NULL,
    job_embedding JSONB,                    -- Vector embedding
    skills_required JSONB,                  -- Array of skills
    experience_required_years FLOAT,
    salary_range_min INTEGER,
    salary_range_max INTEGER,
    location VARCHAR(255),
    employment_type VARCHAR(50),            -- full-time, part-time, etc.
    industry VARCHAR(100),
    job_category VARCHAR(100),
    required_qualifications TEXT,
    status VARCHAR(50) DEFAULT 'active',    -- active, inactive, closed
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Table 2: `candidate_profiles`
Stores candidate profile information and embeddings.

```sql
CREATE TABLE candidate_profiles (
    candidate_id SERIAL PRIMARY KEY,
    candidate_name VARCHAR(255) NOT NULL,
    email_address VARCHAR(255) UNIQUE,
    phone_number VARCHAR(20),
    current_location VARCHAR(255),
    parsed_resume_data JSONB,                -- Full parsed resume
    profile_embedding JSONB,                 -- Vector embedding
    skills JSONB,                            -- Array of skills
    years_of_experience FLOAT,
    current_cgpa FLOAT,
    latest_company VARCHAR(255),
    latest_role_title VARCHAR(255),
    education_degree VARCHAR(100),           -- B.Tech, MBA, etc.
    education_institute VARCHAR(255),
    education_branch VARCHAR(100),
    notice_period_days INTEGER,
    work_authorization VARCHAR(100),
    preferred_roles JSONB,
    employment_type_preference VARCHAR(50),
    status VARCHAR(50) DEFAULT 'active',
    last_updated TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Table 3: `matching_results`
Stores historical matching results and scores.

```sql
CREATE TABLE matching_results (
    match_id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES recruiter_jobs(job_id),
    candidate_id INTEGER REFERENCES candidate_profiles(candidate_id),
    cosine_similarity_score FLOAT,           -- -1 to 1
    match_percentage FLOAT,                  -- 0 to 100
    skill_match_score FLOAT,                 -- 0 to 1
    experience_match_score FLOAT,            -- 0 to 1
    education_match_score FLOAT,             -- 0 to 1
    location_match_score FLOAT,              -- 0 to 1
    final_weighted_score FLOAT,              -- 0 to 1
    match_details JSONB,
    match_status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Indexes for Performance
```sql
CREATE INDEX idx_recruiter_jobs_recruiter_id ON recruiter_jobs(recruiter_id);
CREATE INDEX idx_recruiter_jobs_status ON recruiter_jobs(status);
CREATE INDEX idx_candidate_profiles_email ON candidate_profiles(email_address);
CREATE INDEX idx_candidate_profiles_status ON candidate_profiles(status);
CREATE INDEX idx_matching_results_job_id ON matching_results(job_id);
CREATE INDEX idx_matching_results_candidate_id ON matching_results(candidate_id);
CREATE INDEX idx_matching_results_score ON matching_results(final_weighted_score DESC);
```

---

## 🧠 Matching Algorithm

### Multi-Factor Matching Approach

The system uses a weighted combination of multiple factors to determine match quality:

#### 1. **Embedding Similarity (10%)**
Measures semantic similarity using embeddings.

$$\text{Cosine Similarity} = \frac{\vec{A} \cdot \vec{B}}{|\vec{A}| \times |\vec{B}|}$$

- Range: -1 to +1
- Normalized to 0-1: $(similarity + 1) / 2$

#### 2. **Skill Match Score (35%)**
Calculates intersection of required vs. candidate skills.

$$\text{Skill Match} = \frac{\text{Matched Skills}}{\text{Total Required Skills}}$$

- Performs fuzzy matching for skill variations
- Case-insensitive comparison

#### 3. **Experience Match Score (25%)**
Penalizes underexperience, rewards overexperience.

$$\text{Exp Match} = \begin{cases}
1.0 & \text{if candidate_years} \geq \text{required_years} \\
1.0 - \frac{\text{gap}}{(\text{required} + \text{tolerance})} & \text{if gap} \leq \text{tolerance} \\
0.0 & \text{otherwise}
\end{cases}$$

#### 4. **Education Match Score (20%)**
Compares educational qualifications.

- Degree level matching (PhD > Master > Bachelor > Diploma)
- CGPA bonus if >= 8.5
- Weighs required qualifications

$$\text{Edu Match} = \text{Base Score} + \text{CGPA Bonus}$$

#### 5. **Location Match Score (10%)**
Matches job and candidate locations.

$$\text{Loc Match} = \begin{cases}
1.0 & \text{if exact match} \\
0.8 & \text{if partial match (city/region)} \\
0.6 & \text{if regional match (state/country)} \\
0.3 & \text{otherwise}
\end{cases}$$

#### 6. **Final Composite Score**

$$\text{Final Score} = \sum (\text{Factor Score} \times \text{Weight})$$

$$= \begin{aligned}
&0.10 \times \text{Embedding Sim} + \\
&0.35 \times \text{Skill Match} + \\
&0.25 \times \text{Experience Match} + \\
&0.20 \times \text{Education Match} + \\
&0.10 \times \text{Location Match}
\end{aligned}$$

$$\text{Match Percentage} = \text{Final Score} \times 100$$

### Weights Configuration
All weights are configurable in `config.py` and can be adjusted based on business needs.

### Threshold Filtering
Default minimum threshold: **40%**
- Matches below threshold are filtered out
- Configurable per API call

---

## 📦 Installation

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Google Gemini API key
- pip or conda

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd search-engine-main

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Database Setup

```bash
# Create PostgreSQL database
psql -U postgres -c "CREATE DATABASE campushire_db ENCODING 'UTF8';"

# Optional: Create dedicated user
psql -U postgres -c "CREATE USER campushire WITH PASSWORD 'secure_password';"
psql -U postgres -c "ALTER ROLE campushire SET client_encoding TO 'utf8';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE campushire_db TO campushire;"
```

### Step 4: Configuration

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
# - DB_PASSWORD: PostgreSQL password
# - GEMINI_API_KEY: From Google AI Studio
# - MY_API_AUTH_KEY: Your custom API key
```

### Step 5: Run Application

```bash
# Development mode
python main.py

# Production mode (with gunicorn)
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

Application will be available at: `http://localhost:8080`
API Documentation: `http://localhost:8080/docs`

---

## 🔐 Configuration

### Environment Variables (.env file)

```dotenv
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=campushire_db
DB_USER=postgres
DB_PASSWORD=your_password

# API Keys
GEMINI_API_KEY=your_gemini_key
MY_API_AUTH_KEY=your_secret_key

# Matching Weights (sum must equal 1.0)
EMBEDDINGS_SIMILARITY_WEIGHT=0.10
SKILLS_MATCH_WEIGHT=0.35
EXPERIENCE_MATCH_WEIGHT=0.25
EDUCATION_MATCH_WEIGHT=0.20
LOCATION_MATCH_WEIGHT=0.10

# Thresholds
MIN_SIMILARITY_THRESHOLD=0.4
DEFAULT_TOP_K=10
```

### Config File (`config.py`)

The `config.py` file centralizes all configuration:

```python
from config import (
    DATABASE_CONFIG,
    GEMINI_API_KEY,
    MATCHING_WEIGHTS,
    MIN_SIMILARITY_THRESHOLD,
    DEFAULT_TOP_K
)
```

---

## 📡 API Documentation

### Authentication

All endpoints require the `X-API-Key` header:

```bash
curl -H "X-API-Key: your_secret_key" http://localhost:8080/api/v1/recruiter/health
```

### Base URL

```
http://localhost:8080/api/v1
```

### Complete API Endpoints

#### Recruiter Endpoints

**1. Create Job Posting**
```http
POST /recruiter/jobs/create
Content-Type: application/json
X-API-Key: your_api_key

{
  "recruiter_id": "recruiter_123",
  "job_title": "Senior Python Developer",
  "job_description": "We are looking for...",
  "skills_required": ["Python", "FastAPI", "PostgreSQL", "Docker"],
  "experience_required_years": 5,
  "salary_range_min": 1200000,
  "salary_range_max": 1800000,
  "location": "bangalore",
  "employment_type": "full-time",
  "industry": "Technology",
  "job_category": "Software Development",
  "required_qualifications": "B.Tech/M.Tech in CS or related"
}
```

**Response:**
```json
{
  "status": "success",
  "job_id": 1,
  "message": "Job posting created successfully. Job ID: 1",
  "next_step": "Post to /recruiter/jobs/embed to generate embeddings"
}
```

**2. Generate Job Embedding**
```http
POST /recruiter/jobs/embed
X-API-Key: your_api_key

{
  "job_id": 1
}
```

**Response:**
```json
{
  "status": "success",
  "job_id": 1,
  "embedding_dimension": 768,
  "message": "Job embedding generated and stored successfully"
}
```

**3. Get Job Details**
```http
GET /recruiter/jobs/1
X-API-Key: your_api_key
```

**4. List Recruiter's Jobs**
```http
GET /recruiter/jobs?recruiter_id=recruiter_123&limit=20&offset=0
X-API-Key: your_api_key
```

**5. Update Job Status**
```http
PUT /recruiter/jobs/1/status?status=inactive
X-API-Key: your_api_key
```

#### Candidate Endpoints

**1. Parse Resume**
```http
POST /candidate/profile/parse
X-API-Key: your_api_key
Content-Type: application/json

{
  "resume_text": "JOHN DOE\nEmail: john@example.com\nPhone: +91-9876543210\n\nEDUCATION\nB.Tech in Computer Science\nIndian Institute of Technology\nGPA: 8.5/10\n\nEXPERIENCE\nSenior Developer at TechCorp\n5 years of experience\n\nSKILLS\nPython, Java, AWS, Docker, PostgreSQL"
}
```

**Response:**
```json
{
  "status": "success",
  "parsed_data": {
    "candidate_information": {
      "contact_details": {
        "full_name": "John Doe",
        "email_address": "john@example.com",
        "phone_number": "+91-9876543210"
      },
      "education_snapshot": {
        "college_university": "Indian Institute of Technology",
        "degree_branch": "B.Tech - Computer Science",
        "cgpa_percentage": "8.5"
      },
      ...
    },
    "skills": ["Python", "Java", "AWS", "Docker", "PostgreSQL"],
    ...
  },
  "message": "Resume parsed successfully"
}
```

**2. Create Candidate Profile**
```http
POST /candidate/profile/create
X-API-Key: your_api_key
Content-Type: application/json

{
  "candidate_name": "John Doe",
  "email_address": "john@example.com",
  "phone_number": "+91-9876543210",
  "current_location": "bangalore",
  "skills": ["Python", "Java", "AWS", "Docker", "PostgreSQL"],
  "years_of_experience": 5,
  "current_cgpa": 8.5,
  "latest_company": "TechCorp",
  "latest_role_title": "Senior Developer",
  "education_degree": "B.Tech",
  "education_institute": "Indian Institute of Technology",
  "education_branch": "Computer Science",
  "notice_period_days": 30,
  "work_authorization": "Indian National",
  "preferred_roles": ["Senior Developer", "Tech Lead", "Architect"],
  "employment_type_preference": "full-time"
}
```

**Response:**
```json
{
  "status": "success",
  "candidate_id": 1,
  "message": "Candidate profile created successfully. ID: 1",
  "next_step": "Post to /candidate/profile/embed to generate embeddings"
}
```

**3. Generate Candidate Embedding**
```http
POST /candidate/profile/embed
X-API-Key: your_api_key

{
  "candidate_id": 1
}
```

**4. Get Candidate Profile**
```http
GET /candidate/profile/1
X-API-Key: your_api_key
```

**5. List Candidates**
```http
GET /candidate/profiles?limit=20&offset=0&location=bangalore
X-API-Key: your_api_key
```

#### Matching Endpoints

**1. Find Matching Candidates for Job**
```http
POST /match/find-candidates
X-API-Key: your_api_key
Content-Type: application/json

{
  "job_id": 1,
  "top_k": 10,
  "min_threshold": 0.4
}
```

**Response:**
```json
{
  "status": "success",
  "job_id": 1,
  "job_title": "Senior Python Developer",
  "total_candidates_checked": 150,
  "candidates_with_embeddings": 120,
  "matches_found": 8,
  "top_k_requested": 10,
  "min_threshold_used": 0.4,
  "matches": [
    {
      "candidate_id": 5,
      "candidate_name": "John Doe",
      "email_address": "john@example.com",
      "scores": {
        "cosine_similarity_score": 0.8234,
        "skill_match_score": 0.9,
        "experience_match_score": 1.0,
        "education_match_score": 0.85,
        "location_match_score": 1.0,
        "final_weighted_score": 0.91,
        "match_percentage": 91.0
      },
      "candidate_summary": {
        "name": "John Doe",
        "location": "bangalore",
        "experience": 5,
        "degree": "B.Tech",
        "cgpa": 8.5,
        "skills": ["Python", "Java", "AWS", "Docker", "PostgreSQL"],
        "latest_company": "TechCorp",
        "latest_role": "Senior Developer"
      }
    },
    ...
  ],
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

**2. Find Matching Jobs for Candidate**
```http
POST /match/find-jobs
X-API-Key: your_api_key

{
  "candidate_id": 1,
  "top_k": 10
}
```

**3. Get Job Match History**
```http
GET /match/job/1/results?limit=50
X-API-Key: your_api_key
```

**4. Get Candidate Match History**
```http
GET /match/candidate/1/results?limit=50
X-API-Key: your_api_key
```

#### Health Check Endpoints

```http
GET /health
GET /recruiter/health
GET /candidate/health
GET /match/health
```

---

## 📋 Complete Workflow

### End-to-End Workflow Example

#### Step 1: Recruiter Creates Job

```bash
curl -X POST "http://localhost:8080/api/v1/recruiter/jobs/create" \
  -H "X-API-Key: secret_key" \
  -H "Content-Type: application/json" \
  -d '{
    "recruiter_id": "recruiter_acme",
    "job_title": "Senior Python Developer",
    "job_description": "We are seeking a Senior Python Developer with 5+ years experience...",
    "skills_required": ["Python", "FastAPI", "PostgreSQL", "Docker"],
    "experience_required_years": 5,
    "location": "bangalore",
    "employment_type": "full-time",
    "required_qualifications": "B.Tech in CS or related field"
  }'
```

Returns: `job_id = 42`

#### Step 2: Generate Job Embedding

```bash
curl -X POST "http://localhost:8080/api/v1/recruiter/jobs/embed" \
  -H "X-API-Key: secret_key" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 42
  }'
```

#### Step 3: Candidate Uploads Resume (Parse)

```bash
curl -X POST "http://localhost:8080/api/v1/candidate/profile/parse" \
  -H "X-API-Key: secret_key" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "[Full resume text here]"
  }'
```

Returns: Parsed resume data

#### Step 4: Create Candidate Profile

```bash
curl -X POST "http://localhost:8080/api/v1/candidate/profile/create" \
  -H "X-API-Key: secret_key" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_name": "Alice Johnson",
    "email_address": "alice@example.com",
    "current_location": "bangalore",
    "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
    "years_of_experience": 6,
    "current_cgpa": 8.7,
    "education_degree": "B.Tech",
    "education_institute": "BITS Pilani",
    ...
  }'
```

Returns: `candidate_id = 78`

#### Step 5: Generate Candidate Embedding

```bash
curl -X POST "http://localhost:8080/api/v1/candidate/profile/embed" \
  -H "X-API-Key: secret_key" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": 78
  }'
```

#### Step 6: Find Matching Candidates (Recruiter View)

```bash
curl -X POST "http://localhost:8080/api/v1/match/find-candidates" \
  -H "X-API-Key: secret_key" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 42,
    "top_k": 10,
    "min_threshold": 0.4
  }'
```

Returns: Top 10 matching candidates with scores

#### Step 7: Find Matching Jobs (Candidate View)

```bash
curl -X POST "http://localhost:8080/api/v1/match/find-jobs" \
  -H "X-API-Key: secret_key" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": 78,
    "top_k": 10
  }'
```

Returns: Top 10 matching jobs

#### Step 8: Retrieve Match History

```bash
curl -X GET "http://localhost:8080/api/v1/match/job/42/results?limit=50" \
  -H "X-API-Key: secret_key"
```

---

## 🛠️ Development

### Project Structure

```
search-engine-main/
├── main.py                      # Application entry point
├── config.py                    # Centralized configuration
├── database.py                  # Database operations
├── embedding_utils.py           # Embedding and matching logic
├── auth.py                      # API authentication
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── Dockerfile                   # Docker configuration
├── routers/
│   ├── __init__.py
│   ├── recruiter.py            # Recruiter operations
│   ├── candidate.py            # Candidate operations
│   ├── matching.py             # Matching operations
│   ├── profileparser.py        # Legacy: Resume parsing
│   ├── vector.py               # Legacy: Vector operations
│   ├── vector_storage.py       # Legacy: Vector storage
│   └── candidate_matching.py   # Legacy: Matching logic
├── Test/                        # Test cases
└── README.md                    # This file
```

### Key Files and Their Responsibilities

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app initialization, route registration, startup events |
| `config.py` | All configuration, API keys, matching weights, thresholds |
| `database.py` | Database connection management, schema creation, CRUD operations |
| `embedding_utils.py` | Gemini API calls, embedding generation, similarity calculations, matching algorithms |
| `auth.py` | API key validation middleware |
| `routers/recruiter.py` | Job creation, listing, embedding, status management |
| `routers/candidate.py` | Resume parsing, profile creation, embedding, listing |
| `routers/matching.py` | Find candidates for jobs, find jobs for candidates, retrieve history |

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest Test/test_main.py -v
```

### Code Quality

```bash
# Format code
black .

# Check code style
flake8 .

# Sort imports
isort .

# Type checking
mypy .
```

---

## 🚀 Deployment

### Docker Deployment

**Build Docker image:**
```bash
docker build -t campushire:latest .
```

**Run Docker container:**
```bash
docker run -p 8080:8080 \
  -e DB_HOST=db_host \
  -e DB_PASSWORD=password \
  -e GEMINI_API_KEY=key \
  campushire:latest
```

### Google Cloud Run Deployment

```bash
# Deploy to Cloud Run
gcloud run deploy campushire \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars DB_HOST=ip,DB_PASSWORD=pwd,GEMINI_API_KEY=key
```

### Environment Variables for Production

Ensure these are set:
- `DB_HOST`: Database host
- `DB_PASSWORD`: Database password
- `GEMINI_API_KEY`: Gemini API key
- `MY_API_AUTH_KEY`: Strong API key
- `ENVIRONMENT`: Set to "production"
- `DEBUG_MODE`: Set to "false"

### Security Checklist

- ✅ Change default API key
- ✅ Use strong database password
- ✅ Enable HTTPS in production
- ✅ Configure CORS properly
- ✅ Use environment-specific configs
- ✅ Enable database authentication
- ✅ Set up monitoring and logging
- ✅ Regular security updates

---

## 📊 Performance Optimization

### Database Optimization
- Indexes created on frequently queried columns
- JSONB indexing for embedding queries (if using pgvector)
- Connection pooling recommended for production

### API Optimization
- Top-K retrieval limits results returned
- Batch embedding generation for multiple items
- Caching of candidate/job data (can be added)

### Scaling Recommendations
1. Use connection pooling (PgBouncer)
2. Implement request rate limiting
3. Cache embeddings if frequently reused
4. Use CDN for static content
5. Implement horizontal scaling with load balancer

---

## 🐛 Troubleshooting

### Database Connection Issues

```
Error: Database connection failed
- Check DB_HOST, DB_USER, DB_PASSWORD
- Verify PostgreSQL is running
- Check network connectivity
```

### Embedding Generation Failed

```
Error: Embedding generation failed
- Verify GEMINI_API_KEY is set correctly
- Check Gemini API quota
- Verify internet connectivity
```

### Resume Parsing Issues

```
Error: Resume parsing returned invalid JSON
- Ensure resume text is valid
- Check Gemini API is responding
- Verify text encoding (UTF-8)
```

---

## 📚 Additional Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Google Gemini API Docs](https://ai.google.dev/)
- [NumPy Documentation](https://numpy.org/doc/)

### Related Concepts
- Semantic Search
- Embedding Vectors
- Cosine Similarity
- Multi-factor Scoring
- JSONB in PostgreSQL

---

## 📞 Support and Contact

For issues, bugs, or feature requests, please create an issue in the repository.

---

## 📄 License

This project is part of CampusHire's recruitment platform.

---

## 🎯 Future Enhancements

- [ ] Advanced filtering with ElasticSearch
- [ ] Real-time notification system
- [ ] Interview scheduling integration
- [ ] Skill assessment tests
- [ ] Salary prediction model
- [ ] Interview feedback analysis
- [ ] ATS (Applicant Tracking System) integration
- [ ] Mobile application
- [ ] Analytics dashboard

---

**Version:** 1.0.0  
**Last Updated:** January 2024  
**Status:** Production Ready
