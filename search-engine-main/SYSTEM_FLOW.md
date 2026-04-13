# CampusHire System Flow Documentation

## 📌 Complete System Flow Guide

This document provides a detailed walkthrough of all system flows with exact API calls, data transformations, and algorithmic processes.

---

## 🔄 FLOW 1: RECRUITER JOB POSTING FLOW

### Overview
A recruiter creates a job posting, which is then processed to generate an AI embedding for similarity matching.

### Step-by-Step Process

#### 1.1: Recruiter Creates Job Posting

**API Endpoint:**
```
POST /api/v1/recruiter/jobs/create
```

**Request Body:**
```json
{
  "recruiter_id": "recruiter_acme_001",
  "job_title": "Senior Full-Stack Developer",
  "job_description": "We are seeking a Senior Full-Stack Developer needed with expertise in modern web technologies...",
  "skills_required": [
    "Python",
    "FastAPI",
    "React",
    "PostgreSQL",
    "Docker",
    "Kubernetes",
    "AWS",
    "Git"
  ],
  "experience_required_years": 5,
  "salary_range_min": 1200000,
  "salary_range_max": 1800000,
  "location": "Bangalore",
  "employment_type": "full-time",
  "industry": "Technology",
  "job_category": "Software Development",
  "required_qualifications": "B.Tech/M.Tech in CS or 5+ years of professional experience"
}
```

**Processing in Backend:**
```python
# 1. Validate request data
# 2. Create job record in database
job_data = {
    'recruiter_id': request.recruiter_id,
    'job_title': request.job_title,
    'job_description': request.job_description,
    # ... other fields
}

# 3. Insert into recruiter_jobs table
job_id = create_job_posting(recruiter_id, job_data)
# Returns: job_id = 42
```

**Database State After Step 1:**
```sql
INSERT INTO recruiter_jobs (recruiter_id, job_title, job_description, ...)
VALUES ('recruiter_acme_001', 'Senior Full-Stack Developer', '...', ...)
-- job_id = 42 (auto-generated)
-- job_embedding = NULL (not yet generated)
-- status = 'active'
-- created_at = NOW()
```

**Response:**
```json
{
  "status": "success",
  "job_id": 42,
  "message": "Job posting created successfully. Job ID: 42",
  "next_step": "Post to /recruiter/jobs/embed to generate embeddings"
}
```

---

#### 1.2: Generate Job Embedding

**API Endpoint:**
```
POST /api/v1/recruiter/jobs/embed
```

**Request Body:**
```json
{
  "job_id": 42
}
```

**Processing in Backend:**

```python
# 1. Retrieve job from database
job = get_job_by_id(job_id=42)
# Result: job dictionary with all fields

# 2. Prepare text for embedding
job_text_parts = [
    job['job_title'],  # "Senior Full-Stack Developer"
    job['job_description'],  # Full description
    "Required Skills: " + ", ".join(job['skills_required'])  # "Required Skills: Python, FastAPI, ..."
]
comprehensive_text = " ".join(job_text_parts)

# 3. Call Gemini API to generate embedding
response = genai_client.models.embed_content(
    model="gemini-embedding-001",
    contents=comprehensive_text,
    config={'output_dimensionality': 768}
)
embedding = response.embeddings[0].values
# Returns: List of 768 floats representing the semantic meaning
```

**Embedding Generation Process:**
```
Input Text:
"Senior Full-Stack Developer We are seeking a Senior Full-Stack Developer... Required Skills: Python, FastAPI, React, PostgreSQL, Docker, Kubernetes, AWS, Git"

Gemini API Processing:
- Tokenizes text
- Passes through transformer model
- Generates 768-dimensional vector representing semantic content
- Ensures closely related job postings have similar embeddings

Output: [0.234, -0.156, 0.892, ... 768 values ...] (normalized)
```

**Database Update:**
```sql
UPDATE recruiter_jobs
SET job_embedding = '[0.234, -0.156, 0.892, ...]'::jsonb,
    updated_at = NOW()
WHERE job_id = 42;
```

**Response:**
```json
{
  "status": "success",
  "job_id": 42,
  "embedding_dimension": 768,
  "message": "Job embedding generated and stored successfully"
}
```

---

## 👤 FLOW 2: CANDIDATE PROFILE CREATION FLOW

### Overview
A candidate uploads resume, which is parsed to extract structured data, and then an embedding is generated for matching.

### Step-by-Step Process

#### 2.1: Parse Resume

**API Endpoint:**
```
POST /api/v1/candidate/profile/parse
```

**Request Body:**
```json
{
  "resume_text": "JOHN DOE\nEmail: john@example.com\nPhone: +91-9876543210\n\nObjective:\nSeeking a challenging position in Full-Stack Development\n\nEducation:\nB.Tech in Computer Science\nIndian Institute of Technology Bombay\nGPA: 8.5/10\nGraduation Year: 2019\n\nProfessional Experience:\nSenior Developer at TechCorp Solutions (2020-Present)\n- Developed backend APIs using FastAPI and Python\n- Managed PostgreSQL databases\n- Deployed applications on AWS and Docker\n- Led a team of 3 junior developers\nExperience: 4.5 years\n\nSkills:\n- Programming: Python, JavaScript, Java\n- Frameworks: FastAPI, React, Django\n- Databases: PostgreSQL, MongoDB\n- DevOps: Docker, Kubernetes, AWS\n- Tools: Git, JIRA, Linux\n\nProjects:\n1. E-commerce Platform\n   - Built scalable backend using FastAPI\n   - Implemented real-time features with WebSockets\n\n2. ML Pipeline System\n   - Designed data processing pipeline\n   - Used Python and Pandas for data manipulation\n\nCertifications:\n- AWS Solutions Architect Associate\n- Docker Certified Associate\n\nLinks:\n- GitHub: github.com/johndoe\n- LinkedIn: linkedin.com/in/johndoe"
}
```

**Gemini Parsing Process:**

```python
# 1. Create prompt for Gemini with the desired structure
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
    "skills": [],
    "projects": [...],
    "achievements_certifications": [...],
    "public_links": {...}
}

# 2. Gemini processes resume and extracts structured data
# 3. Returns valid JSON
```

**Parsed Output:**
```json
{
  "candidate_information": {
    "contact_details": {
      "full_name": "John Doe",
      "email_address": "john@example.com",
      "phone_number": "+91-9876543210",
      "current_location": "Mumbai, India"
    },
    "education_snapshot": {
      "college_university": "Indian Institute of Technology Bombay",
      "degree_branch": "B.Tech in Computer Science",
      "graduation_year": "2019",
      "cgpa_percentage": "8.5"
    },
    "professional_summary": "Senior Developer with 4.5 years of experience in Full-Stack Development"
  },
  "work_preferences": {
    "preferred_roles": "Senior Developer, Tech Lead, Architect",
    "employment_type": "Full-time",
    "notice_period_availability": "30 days",
    "work_authorization": "Indian National"
  },
  "experience_snapshot": {
    "latest_company": "TechCorp Solutions",
    "role_title": "Senior Developer",
    "years_of_experience": "4.5",
    "current_ctc": "Not specified"
  },
  "skills": [
    "Python", "JavaScript", "Java", "FastAPI", "React", "Django",
    "PostgreSQL", "MongoDB", "Docker", "Kubernetes", "AWS", "Git"
  ],
  "projects": [
    {
      "project_title": "E-commerce Platform",
      "description": "Built scalable backend using FastAPI",
      "technologies_used": ["FastAPI", "Python", "PostgreSQL"],
      "role": "Backend Developer",
      "duration": "6 months"
    },
    {
      "project_title": "ML Pipeline System",
      "description": "Designed data processing pipeline",
      "technologies_used": ["Python", "Pandas"],
      "role": "Data Engineer"
    }
  ],
  "achievements_certifications": [
    {
      "title": "AWS Solutions Architect Associate",
      "issuer": "Amazon",
      "year": "2023"
    },
    {
      "title": "Docker Certified Associate",
      "issuer": "Docker",
      "year": "2022"
    }
  ],
  "public_links": {
    "github_code_repo": "github.com/johndoe",
    "linkedin": "linkedin.com/in/johndoe"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "parsed_data": {...},
  "message": "Resume parsed successfully. Review and create profile using /candidate/profile/create"
}
```

---

#### 2.2: Create Candidate Profile

**API Endpoint:**
```
POST /api/v1/candidate/profile/create
```

**Request Body (Using Parsed Data):**
```json
{
  "candidate_name": "John Doe",
  "email_address": "john@example.com",
  "phone_number": "+91-9876543210",
  "current_location": "Mumbai",
  "skills": [
    "Python", "JavaScript", "Java", "FastAPI", "React", "Django",
    "PostgreSQL", "MongoDB", "Docker", "Kubernetes", "AWS", "Git"
  ],
  "years_of_experience": 4.5,
  "current_cgpa": 8.5,
  "latest_company": "TechCorp Solutions",
  "latest_role_title": "Senior Developer",
  "education_degree": "B.Tech",
  "education_institute": "Indian Institute of Technology Bombay",
  "education_branch": "Computer Science",
  "notice_period_days": 30,
  "work_authorization": "Indian National",
  "preferred_roles": ["Senior Developer", "Tech Lead", "Architect"],
  "employment_type_preference": "full-time"
}
```

**Database Insertion:**
```sql
INSERT INTO candidate_profiles (
    candidate_name, email_address, phone_number, current_location,
    skills, years_of_experience, current_cgpa, latest_company,
    latest_role_title, education_degree, education_institute,
    education_branch, notice_period_days, work_authorization,
    preferred_roles, employment_type_preference, status, created_at
) VALUES (
    'John Doe', 'john@example.com', '+91-9876543210', 'Mumbai',
    '["Python", "JavaScript", ...]'::jsonb, 4.5, 8.5, 'TechCorp Solutions',
    'Senior Developer', 'B.Tech', 'Indian Institute of Technology Bombay',
    'Computer Science', 30, 'Indian National',
    '["Senior Developer", "Tech Lead", "Architect"]'::jsonb, 'full-time',
    'active', NOW()
)
RETURNING candidate_id;
-- Returns: candidate_id = 78
```

**Response:**
```json
{
  "status": "success",
  "candidate_id": 78,
  "message": "Candidate profile created successfully. ID: 78",
  "next_step": "Post to /candidate/profile/embed to generate embeddings"
}
```

---

#### 2.3: Generate Candidate Embedding

**API Endpoint:**
```
POST /api/v1/candidate/profile/embed
```

**Request Body:**
```json
{
  "candidate_id": 78
}
```

**Processing:**

```python
# 1. Retrieve candidate data
candidate = get_candidate_by_id(candidate_id=78)

# 2. Format candidate data to readable text
text_parts = [
    "Name: John Doe",
    "Experience: 4.5 years",
    "Skills: Python, JavaScript, Java, FastAPI, React, Django, PostgreSQL, MongoDB, Docker, Kubernetes, AWS, Git",
    "Latest Role: Senior Developer",
    "Latest Company: TechCorp Solutions",
    "Degree: B.Tech in Computer Science",
    "Institution: Indian Institute of Technology Bombay",
    "CGPA: 8.5",
    "Preferred Roles: Senior Developer, Tech Lead, Architect"
]
comprehensive_text = " ".join(text_parts)

# 3. Generate embedding using Gemini
embedding = generate_embedding(comprehensive_text)
# Returns: List of 768 floats
```

**Candidate Embedding Text:**
```
Name: John Doe Experience: 4.5 years Skills: Python, JavaScript, Java, FastAPI, React, Django, PostgreSQL, MongoDB, Docker, Kubernetes, AWS, Git Latest Role: Senior Developer Latest Company: TechCorp Solutions Degree: B.Tech in Computer Science Institution: Indian Institute of Technology Bombay CGPA: 8.5 Preferred Roles: Senior Developer, Tech Lead, Architect
```

**Database Update:**
```sql
UPDATE candidate_profiles
SET profile_embedding = '[0.456, -0.234, 0.789, ...]'::jsonb,
    last_updated = NOW()
WHERE candidate_id = 78;
```

**Response:**
```json
{
  "status": "success",
  "candidate_id": 78,
  "embedding_dimension": 768,
  "message": "Candidate embedding generated and stored successfully"
}
```

---

## 🎯 FLOW 3: MATCHING FLOW - FIND CANDIDATES FOR JOB

### Overview
Recruiter searches for candidates matching a job posting using the AI matching algorithm.

### Step-by-Step Process

#### 3.1: Request Matching

**API Endpoint:**
```
POST /api/v1/match/find-candidates
```

**Request Body:**
```json
{
  "job_id": 42,
  "top_k": 10,
  "min_threshold": 0.4
}
```

#### 3.2: Data Retrieval

**Process:**
```python
# 1. Retrieve job details
job = get_job_by_id(job_id=42)
# Result:
{
    "job_id": 42,
    "job_title": "Senior Full-Stack Developer",
    "job_description": "...",
    "job_embedding": [0.234, -0.156, 0.892, ...],  # 768-dim vector
    "skills_required": ["Python", "FastAPI", "React", "PostgreSQL", "Docker", "Kubernetes", "AWS", "Git"],
    "experience_required_years": 5,
    "location": "Bangalore",
    ...
}

# 2. Verify job has embedding
if not job['job_embedding']:
    raise Error("Job must have embedding first")

# 3. Retrieve all active candidates with embeddings
candidates = get_all_active_candidates()
candidates_with_embeddings = [c for c in candidates if c.get('profile_embedding')]
# Result: List of N candidates with embeddings
```

---

#### 3.3: Matching Algorithm - Score Calculation

For each candidate, calculate composite match score:

**Algorithm Process:**

```python
# For candidate_id = 78 (John Doe)

candidate = {
    "candidate_id": 78,
    "candidate_name": "John Doe",
    "profile_embedding": [0.456, -0.234, 0.789, ...],  # 768-dim
    "skills": ["Python", "JavaScript", "Java", "FastAPI", "React", "Django", "PostgreSQL", "MongoDB", "Docker", "Kubernetes", "AWS", "Git"],
    "years_of_experience": 4.5,
    "current_cgpa": 8.5,
    "education_degree": "B.Tech",
    "current_location": "Mumbai",
    ...
}

# =========================================================================
# 1. EMBEDDING SIMILARITY (Weight: 10%)
# =========================================================================
job_embedding = [0.234, -0.156, 0.892, ...]
candidate_embedding = [0.456, -0.234, 0.789, ...]

# Cosine Similarity Formula: cos(θ) = (A·B) / (||A|| × ||B||)
dot_product = sum(a*b for a,b in zip(job_embedding, candidate_embedding))
# = 0.234*0.456 + (-0.156)*(-0.234) + 0.892*0.789 + ...
# = 0.10694 + 0.03650 + 0.70387 + ...
# = (calculated value)

norm_job = sqrt(sum(x**2 for x in job_embedding))  # ≈ 1.0 (normalized)
norm_candidate = sqrt(sum(x**2 for x in candidate_embedding))  # ≈ 1.0

cosine_similarity = dot_product / (norm_job * norm_candidate)
# Result: 0.8234 (range: -1 to 1)

# Normalize to 0-1 range
embedding_similarity_normalized = (0.8234 + 1) / 2 = 0.9117

# =========================================================================
# 2. SKILL MATCH SCORE (Weight: 35%)
# =========================================================================
job_skills = ["Python", "FastAPI", "React", "PostgreSQL", "Docker", "Kubernetes", "AWS", "Git"]
candidate_skills = ["Python", "JavaScript", "Java", "FastAPI", "React", "Django", "PostgreSQL", "MongoDB", "Docker", "Kubernetes", "AWS", "Git"]

# Count skill matches (including fuzzy matching)
matched_skills = 0
for job_skill in job_skills:
    for candidate_skill in candidate_skills:
        if job_skill.lower() in candidate_skill.lower() or candidate_skill.lower() in job_skill.lower():
            matched_skills += 1
            break

# Results:
# Python ✓, FastAPI ✓, React ✓, PostgreSQL ✓, Docker ✓, Kubernetes ✓, AWS ✓, Git ✓
matched_skills = 8

# Formula: matched_skills / total_required_skills
skill_match_score = 8 / 8 = 1.0 (100% match)

# =========================================================================
# 3. EXPERIENCE MATCH SCORE (Weight: 25%)
# =========================================================================
job_required_years = 5
candidate_years = 4.5
experience_gap = 5 - 4.5 = 0.5

# Candidate is slightly underexperienced but within tolerance
# Formula (with tolerance = 2 years):
if candidate_years >= job_required_years:
    experience_match_score = 1.0  # Perfect match
elif experience_gap <= tolerance:
    experience_match_score = 1.0 - (experience_gap / (job_required_years + tolerance))
    # = 1.0 - (0.5 / (5 + 2))
    # = 1.0 - (0.5 / 7)
    # = 1.0 - 0.0714
    # = 0.9286
else:
    experience_match_score = 0.0

# Result: 0.9286 (93% match due to slight underexperience)

# =========================================================================
# 4. EDUCATION MATCH SCORE (Weight: 20%)
# =========================================================================
job_qualifications = "B.Tech/M.Tech in CS or 5+ years of professional experience"
candidate_degree = "B.Tech"
candidate_cgpa = 8.5

# Degree level mapping
degree_keywords = {
    'phd': 1.0,
    'doctorate': 1.0,
    'master': 0.9,
    'mtech': 0.9,
    'bachelor': 0.8,
    'btech': 0.8,
    'bsc': 0.75,
    'diploma': 0.6
}

# Find matching degree in candidate's degree
base_score = 0.5
for degree_type in degree_keywords:
    if degree_type in candidate_degree.lower():
        if degree_type in job_qualifications.lower():
            base_score = degree_keywords[degree_type]  # 0.8
        break

education_score = 0.8

# Add CGPA bonus (if >= 8.5)
if candidate_cgpa >= 8.5:
    education_score = min(1.0, education_score + 0.1)
    # = min(1.0, 0.8 + 0.1) = 0.9

# Result: 0.9 (90% match with CGPA bonus)

# =========================================================================
# 5. LOCATION MATCH SCORE (Weight: 10%)
# =========================================================================
job_location = "Bangalore"
candidate_location = "Mumbai"

# Different cities but same country
job_loc_lower = "bangalore"
candidate_loc_lower = "mumbai"

if job_loc_lower == candidate_loc_lower:
    location_match = 1.0  # Exact match
elif job_loc_lower in candidate_loc_lower or candidate_loc_lower in job_loc_lower:
    location_match = 0.8  # Partial match
else:
    # Check if same country (both are Indian cities)
    location_match = 0.6  # Same country but different city

# Result: 0.6 (Geographic match but different cities)

# =========================================================================
# 6. FINAL COMPOSITE SCORE CALCULATION
# =========================================================================
weights = {
    'embeddings_similarity': 0.10,
    'skills_match': 0.35,
    'experience_match': 0.25,
    'education_match': 0.20,
    'location_match': 0.10
}

final_score = (
    0.9117 * 0.10 +      # Embedding similarity
    1.0 * 0.35 +         # Skill match
    0.9286 * 0.25 +      # Experience match
    0.9 * 0.20 +         # Education match
    0.6 * 0.10           # Location match
)

# = 0.09117 + 0.35 + 0.23215 + 0.18 + 0.06
# = 0.91332

# Convert to percentage
match_percentage = 0.91332 * 100 = 91.33%

# =========================================================================
# SCORES SUMMARY
# =========================================================================
scores = {
    "cosine_similarity_score": 0.8234,
    "skill_match_score": 1.0,
    "experience_match_score": 0.9286,
    "education_match_score": 0.9,
    "location_match_score": 0.6,
    "final_weighted_score": 0.9133,
    "match_percentage": 91.33
}
```

---

#### 3.4: Threshold Filtering & Sorting

```python
# Filter by threshold
if final_weighted_score >= min_threshold (0.4):
    # Include this match
    matches.append({
        "candidate_id": 78,
        "candidate_name": "John Doe",
        "email_address": "john@example.com",
        "scores": {...},
        "candidate_summary": {...}
    })

# Result: 0.9133 >= 0.4 ✓ (Included)

# Sort by final_weighted_score in descending order
matches.sort(key=lambda x: x['final_weighted_score'], reverse=True)

# Return top K
return matches[:top_k]  # [:10]
```

---

#### 3.5: Database Storage

```python
# Store match result in database
match_data = {
    'job_id': 42,
    'candidate_id': 78,
    'cosine_similarity_score': 0.8234,
    'match_percentage': 91.33,
    'skill_match_score': 1.0,
    'experience_match_score': 0.9286,
    'education_match_score': 0.9,
    'location_match_score': 0.6,
    'final_weighted_score': 0.9133,
    'match_details': {
        'job_title': 'Senior Full-Stack Developer',
        'candidate_name': 'John Doe',
        'matched_at': '2024-01-15T10:30:45'
    }
}

# SQL Insert
INSERT INTO matching_results (
    job_id, candidate_id, cosine_similarity_score, match_percentage,
    skill_match_score, experience_match_score, education_match_score,
    location_match_score, final_weighted_score, match_details, created_at
) VALUES (
    42, 78, 0.8234, 91.33, 1.0, 0.9286, 0.9, 0.6, 0.9133, {...}, NOW()
);
```

---

#### 3.6: Final Response

**Response:**
```json
{
  "status": "success",
  "job_id": 42,
  "job_title": "Senior Full-Stack Developer",
  "total_candidates_checked": 150,
  "candidates_with_embeddings": 120,
  "matches_found": 8,
  "top_k_requested": 10,
  "min_threshold_used": 0.4,
  "matches": [
    {
      "candidate_id": 78,
      "candidate_name": "John Doe",
      "email_address": "john@example.com",
      "scores": {
        "cosine_similarity_score": 0.8234,
        "skill_match_score": 1.0,
        "experience_match_score": 0.9286,
        "education_match_score": 0.9,
        "location_match_score": 0.6,
        "final_weighted_score": 0.9133,
        "match_percentage": 91.33
      },
      "candidate_summary": {
        "name": "John Doe",
        "location": "Mumbai",
        "experience": 4.5,
        "degree": "B.Tech",
        "cgpa": 8.5,
        "skills": ["Python", "JavaScript", "Java", "FastAPI", "React", "Django", "PostgreSQL", "MongoDB", "Docker", "Kubernetes", "AWS", "Git"],
        "latest_company": "TechCorp Solutions",
        "latest_role": "Senior Developer"
      }
    },
    // ... 7 more matches ...
  ],
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

---

## 📊 FLOW 4: REVERSE MATCHING - FIND JOBS FOR CANDIDATE

### Overview
Candidate searches for job opportunities matching their profile using the same algorithm.

### Process
1. Retrieve candidate profile and embedding
2. Retrieve all active jobs with embeddings
3. Calculate composite score for each job
4. Filter by threshold
5. Sort by score
6. Return top K jobs

The process is identical to Flow 3 but in reverse direction (candidate → jobs instead of job → candidates).

---

## 🔄 FLOW 5: RETRIEVE MATCH HISTORY

### Endpoints

**Get all matches for a job:**
```
GET /match/job/42/results?limit=50
```

**Get all matches for a candidate:**
```
GET /match/candidate/78/results?limit=50
```

### Database Query

```sql
-- Query for job matches
SELECT m.*, c.candidate_name, c.email_address
FROM matching_results m
JOIN candidate_profiles c ON m.candidate_id = c.candidate_id
WHERE m.job_id = 42 AND m.match_status = 'active'
ORDER BY m.final_weighted_score DESC
LIMIT 50;
```

---

## 📈 Performance Metrics

### Index Usage

```
- Fast lookup by recruiter_id
- Fast lookup by job status (active/inactive)
- Fast lookup by candidate email
- Fast sorting by match score (DESC)
```

### Query Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Create job | <100ms | Quick insert |
| Generate embedding | 500-2000ms | Depends on Gemini API |
| Match 120 candidates | 5-10s | Linear scan + scoring |
| Retrieve top K | <50ms | Sorted query with limit |
| Store match result | <100ms | Single insert |

---

## 🔐 Data Security

### Sensitive Data Handling

- API Keys stored in `.env` (not in code)
- Database passwords encrypted
- User emails stored securely
- Embeddings stored as JSONB (not transmitted to client)

---

## 📝 Summary

This complete flow documentation shows:
1. ✅ How data enters the system (jobs and resumes)
2. ✅ How embeddings are generated using Google Gemini
3. ✅ How the matching algorithm works (with formulas)
4. ✅ How results are calculated and scored
5. ✅ How data is stored and retrieved
6. ✅ Complete API flow with examples

All components are tightly integrated and follow the exact specifications from the system design.
