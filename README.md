# CampusHire: AI-Powered Recruiter-Candidate Matching System

[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com/campushire)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/license-proprietary-blue)](LICENSE)
[![Status](https://img.shields.io/badge/status-production%20ready-green)](.)

## 🎯 Overview

**CampusHire** is a revolutionary AI-powered platform that intelligently matches job seekers with relevant job opportunities using advanced semantic embedding and multi-factor scoring algorithms.

### Key Capabilities
- 🤖 **AI-Powered Matching** - Uses Google Gemini for semantic understanding
- 📊 **Multi-Factor Scoring** - Combines skills, experience, education, and location
- 📄 **Smart Resume Parsing** - Automatic extraction of candidate information
- ⚡ **Real-Time Matching** - Instant candidate-job match finding
- 📈 **Scalable Architecture** - PostgreSQL + FastAPI + Docker ready

---

## 🚀 Quick Start (5 minutes)

**For the fastest setup, follow this guide:**
```bash
# 1. Clone repository
git clone <repo-url>
cd search-engine-main

# 2. Setup environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 5. Run application
python main.py
```

**Then visit:** http://localhost:8080/docs for API documentation

📖 **See [QUICKSTART.md](QUICKSTART.md) for detailed instructions**

---

## 📚 Documentation

This project includes comprehensive documentation:

| Document | Purpose |
|----------|---------|
| **[QUICKSTART.md](QUICKSTART.md)** | 5-minute setup guide ⭐ START HERE |
| **[README_COMPLETE.md](README_COMPLETE.md)** | Comprehensive documentation (100+ pages) |
| **[SYSTEM_FLOW.md](SYSTEM_FLOW.md)** | Detailed technical workflows with examples |
| **[API_TESTING.md](API_TESTING.md)** | Complete curl commands and testing guide |
| **[PROJECT_COMPLETION_SUMMARY.md](PROJECT_COMPLETION_SUMMARY.md)** | Project overview and deliverables |

---

## 🏗️ Architecture

```
┌─────────────┐
│   Recruiter │
│  Dashboard  │
└──────┬──────┘
       │
       ▼
┌──────────────────────┐
│  FastAPI Backend     │
│  - Recruiter Routes  │
│  - Candidate Routes  │
│  - Matching Routes   │
└──────────┬───────────┘
           │
   ┌───────┴────────┐
   ▼                ▼
┌──────────┐   ┌─────────────┐
│PostgreSQL│   │Google Gemini│
│Database  │   │Embeddings   │
└──────────┘   └─────────────┘
```

---

## 💻 System Components

### Modules Included

```
config.py                    ← Centralized configuration
database.py                  ← PostgreSQL operations
embedding_utils.py           ← Gemini API & matching algorithm
routers/
  ├── recruiter.py          ← Job management endpoints
  ├── candidate.py          ← Profile management endpoints
  └── matching.py           ← Matching algorithm endpoints
main.py                      ← FastAPI application
auth.py                      ← API authentication
```

### 22 API Endpoints

- **5** Recruiter endpoints (job management)
- **6** Candidate endpoints (profile management)
- **4** Matching endpoints (find jobs/candidates)
- **4** Health check endpoints
- **3** System endpoints (root, health, version)

---

## 🎯 Quick Example

### 1️⃣ Create Job
```bash
curl -X POST "http://localhost:8080/api/v1/recruiter/jobs/create" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "recruiter_id": "recruiter_001",
    "job_title": "Senior Python Developer",
    "job_description": "...",
    "skills_required": ["Python", "FastAPI", "PostgreSQL"],
    "experience_required_years": 5,
    "location": "bangalore"
  }'
```

### 2️⃣ Create Candidate
```bash
curl -X POST "http://localhost:8080/api/v1/candidate/profile/create" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_name": "John Doe",
    "email_address": "john@example.com",
    "skills": ["Python", "FastAPI", "PostgreSQL"],
    "years_of_experience": 6,
    "education_degree": "B.Tech",
    "education_institute": "IIT",
    "current_location": "bangalore"
  }'
```

### 3️⃣ Find Matches
```bash
curl -X POST "http://localhost:8080/api/v1/match/find-candidates" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 1,
    "top_k": 10
  }'
```

**Result:** List of matching candidates with scores 0-100%

📖 **See [API_TESTING.md](API_TESTING.md) for complete examples**

---

## 🧠 Matching Algorithm

The system uses a **weighted multi-factor approach**:

```
Final Score = 
    0.10 × Embedding Similarity +
    0.35 × Skill Match +
    0.25 × Experience Match +
    0.20 × Education Match +
    0.10 × Location Match
```

### Individual Factors

| Factor | Weight | Formula |
|--------|--------|---------|
| **Embedding Similarity** | 10% | Cosine(job_embedding, candidate_embedding) |
| **Skill Match** | 35% | matched_skills / required_skills |
| **Experience Match** | 25% | Penalty for underexperience |
| **Education Match** | 20% | Degree level + CGPA consideration |
| **Location Match** | 10% | Exact/partial/regional/country match |

📖 **See [SYSTEM_FLOW.md](SYSTEM_FLOW.md) for detailed formulas and examples**

---

## 🗄️ Database

### Three-Table Architecture

**recruiter_jobs** (Job Postings)
- job_id, recruiter_id, job_title, job_description
- job_embedding (768-D vector), skills_required
- experience_required_years, salary_range, location
- employment_type, industry, status, timestamps

**candidate_profiles** (Candidate Profiles)
- candidate_id, candidate_name, email_address, phone
- current_location, profile_embedding (768-D vector)
- skills, years_of_experience, current_cgpa
- education_degree, education_institute, education_branch
- preferred_roles, employment_type_preference, status, timestamps

**matching_results** (Match History)
- match_id, job_id, candidate_id
- cosine_similarity_score, match_percentage
- skill_match_score, experience_match_score
- education_match_score, location_match_score
- final_weighted_score, match_details, timestamps

📖 **See [README_COMPLETE.md](README_COMPLETE.md) for full schema**

---

## 🔧 Configuration

### Environment Variables (.env)

```dotenv
# Database
DB_HOST=localhost
DB_NAME=campushire_db
DB_USER=postgres
DB_PASSWORD=your_password

# API Keys
GEMINI_API_KEY=your_gemini_key
MY_API_AUTH_KEY=your_secret_key

# Matching Weights
SKILLS_MATCH_WEIGHT=0.35
EXPERIENCE_MATCH_WEIGHT=0.25
EDUCATION_MATCH_WEIGHT=0.20
LOCATION_MATCH_WEIGHT=0.10
EMBEDDINGS_SIMILARITY_WEIGHT=0.10

# Thresholds
MIN_SIMILARITY_THRESHOLD=0.4
DEFAULT_TOP_K=10
```

📖 **See .env.example for complete template**

---

## 📦 Requirements

- Python 3.9+
- PostgreSQL 12+
- Google Gemini API key
- 512MB RAM minimum
- 100MB disk space

### Install Dependencies
```bash
pip install -r requirements.txt
```

**Key packages:**
- FastAPI & Uvicorn (web framework)
- Google Gemini SDK (AI embeddings)
- psycopg2 (PostgreSQL)
- NumPy (vector operations)
- Pydantic (validation)

---

## 🚀 Deployment

### Docker
```bash
docker build -t campushire:latest .
docker run -p 8080:8080 -e DB_HOST=... campushire:latest
```

### Google Cloud Run
```bash
gcloud run deploy campushire --source . --region us-central1 \
  --set-env-vars DB_HOST=...,GEMINI_API_KEY=...
```

📖 **See [README_COMPLETE.md](README_COMPLETE.md) for detailed deployment**

---

## 📊 API Documentation

### Interactive Docs
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

### Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/recruiter/jobs/create` | POST | Create job posting |
| `/api/v1/recruiter/jobs/embed` | POST | Generate job embedding |
| `/api/v1/candidate/profile/parse` | POST | Parse resume |
| `/api/v1/candidate/profile/create` | POST | Create candidate |
| `/api/v1/candidate/profile/embed` | POST | Generate candidate embedding |
| `/api/v1/match/find-candidates` | POST | Find matching candidates for job |
| `/api/v1/match/find-jobs` | POST | Find matching jobs for candidate |

📖 **See [API_TESTING.md](API_TESTING.md) for all endpoints and examples**

---

## 🔐 Security

- ✅ API key authentication
- ✅ Environment-based secrets
- ✅ Input validation (Pydantic)
- ✅ SQL injection prevention
- ✅ CORS protection
- ✅ Error sanitization

---

## 🧪 Testing

Run the API with Swagger UI and test interactively:

1. Start application: `python main.py`
2. Open browser: http://localhost:8080/docs
3. Click "Authorize" and enter your API key
4. Test endpoints directly from the UI

**Or use curl:** See [API_TESTING.md](API_TESTING.md)

---

## 📈 Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Create job | <100ms | Database write |
| Generate embedding | 500-2000ms | Gemini API call |
| Match 100 candidates | 5-10s | Scoring calculation |
| Database query | <50ms | With indexes |

---

## 🤝 Contributing

To contribute to this project:

1. Follow the code structure
2. Use type hints (Pydantic models)
3. Write comprehensive docstrings
4. Test your changes
5. Update documentation

---

## 📝 License

This project is proprietary and confidential.

---

## 📞 Support & Troubleshooting

### Setup Issues
→ See [QUICKSTART.md](QUICKSTART.md)

### API Questions
→ See [API_TESTING.md](API_TESTING.md)

### Architecture Questions
→ See [README_COMPLETE.md](README_COMPLETE.md)

### Workflow Questions
→ See [SYSTEM_FLOW.md](SYSTEM_FLOW.md)

---

## 🎯 Next Steps

1. **Setup** - Follow [QUICKSTART.md](QUICKSTART.md) (5 minutes)
2. **Test** - Use [API_TESTING.md](API_TESTING.md) examples
3. **Explore** - Read [README_COMPLETE.md](README_COMPLETE.md)
4. **Deploy** - Follow deployment guide

---

## ✨ Features Highlights

✅ AI-powered semantic matching  
✅ Resume parsing and extraction  
✅ Multi-factor scoring algorithm  
✅ Configurable matching weights  
✅ Real-time embedding generation  
✅ Match history tracking  
✅ Scalable PostgreSQL design  
✅ Docker deployment ready  
✅ Comprehensive API documentation  
✅ Production-ready code  

---

## 📊 Project Stats

- **Total Lines of Code**: ~2,800 (core + utils)
- **API Endpoints**: 22
- **Database Tables**: 3
- **Matching Factors**: 5+
- **Documentation Pages**: 200+
- **Test Coverage**: Comprehensive examples provided

---

## 🎉 Quick Links

| Resource | Link |
|----------|------|
| 🚀 Quick Start | [QUICKSTART.md](QUICKSTART.md) |
| 📖 Full Documentation | [README_COMPLETE.md](README_COMPLETE.md) |
| 🔄 System Flows | [SYSTEM_FLOW.md](SYSTEM_FLOW.md) |
| 🧪 API Testing | [API_TESTING.md](API_TESTING.md) |
| ✅ Completion Summary | [PROJECT_COMPLETION_SUMMARY.md](PROJECT_COMPLETION_SUMMARY.md) |
| 🌐 API Docs | http://localhost:8080/docs |

---

## 📌 Version Information

- **Version**: 1.0.0
- **Status**: Production Ready ✅
- **Last Updated**: January 2024
- **Python Version**: 3.9+
- **Framework**: FastAPI
- **Database**: PostgreSQL 12+

---

**🚀 Ready to get started?** Follow the [QUICKSTART.md](QUICKSTART.md) guide now!

---

*CampusHire © 2024 - Intelligent Recruitment Platform*
