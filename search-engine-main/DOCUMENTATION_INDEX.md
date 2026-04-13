# Documentation Index

Welcome to CampusHire! This guide helps you navigate through all available documentation.

---

## 🚀 Quick Navigation

### I want to...

**...get started immediately (local development)**
→ [QUICKSTART.md](QUICKSTART.md)

**...deploy to Google Cloud Run**  
→ [CLOUD_RUN_SETUP.md](CLOUD_RUN_SETUP.md)

**...understand the configuration and secrets**
→ [CONFIGURATION.md](CONFIGURATION.md)

**...test the APIs**
→ [API_TESTING.md](API_TESTING.md)

**...understand the architecture and algorithms**
→ [SYSTEM_FLOW.md](SYSTEM_FLOW.md) + [README_COMPLETE.md](README_COMPLETE.md)

**...understand the Cloud Run migration**
→ [CLOUD_RUN_MIGRATION.md](CLOUD_RUN_MIGRATION.md)

**...see project completion details**
→ [PROJECT_COMPLETION_SUMMARY.md](PROJECT_COMPLETION_SUMMARY.md)

---

## 📋 Complete Documentation Map

### Getting Started

| Document | Purpose | Audience | Time |
|----------|---------|----------|------|
| [README.md](README.md) | Overview & project intro | Everyone | 5 min |
| [QUICKSTART.md](QUICKSTART.md) | 5-minute local setup | Developers | 10 min |
| [CLOUD_RUN_MIGRATION.md](CLOUD_RUN_MIGRATION.md) | Architecture overview | Everyone | 10 min |

### Configuration & Deployment

| Document | Purpose | Audience | Time |
|----------|---------|----------|------|
| [CONFIGURATION.md](CONFIGURATION.md) | Secrets & config management | DevOps/Developers | 15 min |
| [CLOUD_RUN_SETUP.md](CLOUD_RUN_SETUP.md) | Production deployment guide | DevOps | 20 min |
| [.env.local.example](.env.local.example) | Local environment template | Developers | Reference |
| [Dockerfile](Dockerfile) | Container configuration | DevOps | Reference |

### Development & Testing

| Document | Purpose | Audience | Time |
|----------|---------|----------|------|
| [API_TESTING.md](API_TESTING.md) | How to test API endpoints | Developers/QA | 15 min |
| [SYSTEM_FLOW.md](SYSTEM_FLOW.md) | System architecture & flows | Developers | 20 min |
| [README_COMPLETE.md](README_COMPLETE.md) | Full system documentation | Developers | 30 min |

### Project Information

| Document | Purpose | Audience | Time |
|----------|---------|----------|------|
| [PROJECT_COMPLETION_SUMMARY.md](PROJECT_COMPLETION_SUMMARY.md) | Implementation details | Project Managers | 15 min |

---

## 🎯 Documentation by Role

### 👨‍💻 Backend Developer (Local Development)

1. Start: [README.md](README.md) - 5 min overview
2. Setup: [QUICKSTART.md](QUICKSTART.md) - Get running locally
3. Config: [CONFIGURATION.md](CONFIGURATION.md) - Understand secrets
4. Testing: [API_TESTING.md](API_TESTING.md) - Test your changes
5. Deep-dive: [SYSTEM_FLOW.md](SYSTEM_FLOW.md) - Understand architecture

**Quick commands:**
```bash
cp .env.local.example .env
pip install -r requirements.txt
python main.py
```

### 🚀 DevOps/Cloud Engineer (Production Deployment)

1. Start: [CLOUD_RUN_MIGRATION.md](CLOUD_RUN_MIGRATION.md) - Understand setup
2. Deploy: [CLOUD_RUN_SETUP.md](CLOUD_RUN_SETUP.md) - Deploy to Cloud Run
3. Config: [CONFIGURATION.md](CONFIGURATION.md) - Manage secrets
4. Monitor: View logs in Google Cloud Console

**Quick commands:**
```bash
gcloud secrets list
gcloud run logs read search-engine-api --follow
git push origin main  # Auto-deploys via GitHub Actions
```

### 📊 Project Manager / Stakeholder

1. Overview: [README.md](README.md)
2. Status: [PROJECT_COMPLETION_SUMMARY.md](PROJECT_COMPLETION_SUMMARY.md)
3. Architecture: [SYSTEM_FLOW.md](SYSTEM_FLOW.md)
4. Technical: [CLOUD_RUN_MIGRATION.md](CLOUD_RUN_MIGRATION.md)

### 🧪 QA / Tester

1. Start: [QUICKSTART.md](QUICKSTART.md) - Set up local environment
2. Testing: [API_TESTING.md](API_TESTING.md) - Complete testing guide
3. Flows: [SYSTEM_FLOW.md](SYSTEM_FLOW.md) - Understand test scenarios

---

## 📁 File Structure

```
search-engine-main/
├── 📄 README.md (START HERE)
├── 📄 QUICKSTART.md (Local dev setup)
├── 📄 CLOUD_RUN_SETUP.md (Production deployment)
├── 📄 CONFIGURATION.md (Secrets management)
├── 📄 CLOUD_RUN_MIGRATION.md (Architecture overview)
├── 📄 API_TESTING.md (API testing guide)
├── 📄 SYSTEM_FLOW.md (Algorithm details)
├── 📄 README_COMPLETE.md (Full documentation)
├── 📄 PROJECT_COMPLETION_SUMMARY.md (Implementation status)
│
├── 🐍 main.py (FastAPI application entry point)
├── 🐍 config.py (Centralized configuration)
├── 🐍 database.py (Database operations)
├── 🐍 embedding_utils.py (Gemini API integration)
├── 🐍 auth.py (Authentication)
├── 🐍 requirements.txt (Python dependencies)
│
├── 📁 routers/
│   ├── recruiter.py (Job posting endpoints)
│   ├── candidate.py (Candidate profile endpoints)
│   ├── matching.py (Matching algorithm endpoints)
│   └── ...
│
├── 🐳 Dockerfile (Container configuration)
├── 📝 .env.local.example (Local environment template)
├── 📝 .env.example (Configuration template)
├── 📝 .gitignore (Git ignored files)
│
└── 📁 Test/ (Test files)
```

---

## 🔄 Common Workflows

### Workflow 1: Local Development

```
1. Read: QUICKSTART.md
2. Create: .env file (from .env.local.example)
3. Install: pip install -r requirements.txt
4. Run: python main.py
5. Test: Open http://localhost:8080/docs
6. Reference: API_TESTING.md for test flows
```

### Workflow 2: First Cloud Deployment

```
1. Read: CLOUD_RUN_MIGRATION.md
2. Read: CLOUD_RUN_SETUP.md
3. Setup: Create secrets in Google Secret Manager
4. Deploy: git push origin main
5. Monitor: View logs in Cloud Console
6. Reference: CONFIGURATION.md for troubleshooting
```

### Workflow 3: Making Changes

```
1. Make code changes locally
2. Test: python main.py (with .env file)
3. Test APIs: Use curl or Swagger at /docs
4. Commit: git add . && git commit -m "..."
5. Deploy: git push origin main
6. Verify: gcloud run logs read search-engine-api
```

### Workflow 4: Debugging Issues

```
1. Local issues:
   └─ Check: QUICKSTART.md troubleshooting
   └─ Check: CONFIGURATION.md

2. Cloud issues:
   └─ Check: CLOUD_RUN_SETUP.md troubleshooting
   └─ View logs: gcloud run logs read search-engine-api --follow
   
3. API issues:
   └─ Check: API_TESTING.md
   └─ Test endpoints: http://localhost:8080/docs (local)
```

---

## 🆘 Troubleshooting Guide

### Problem: "Module not found"

→ [QUICKSTART.md](QUICKSTART.md) - Step 3: Install Dependencies

### Problem: "Database connection refused"

→ [CONFIGURATION.md](CONFIGURATION.md) - Troubleshooting section

### Problem: "Invalid API Key"

→ [CONFIGURATION.md](CONFIGURATION.md) - Local Development Setup

### Problem: "Cloud Run deployment failed"

→ [CLOUD_RUN_SETUP.md](CLOUD_RUN_SETUP.md) - Troubleshooting section

### Problem: "Secret not found in Cloud Run"

→ [CLOUD_RUN_SETUP.md](CLOUD_RUN_SETUP.md) - Issue: "Secret not found" Error

### Problem: "Don't understand the architecture"

→ [SYSTEM_FLOW.md](SYSTEM_FLOW.md) - Architecture overview

---

## 📊 API Documentation

### Interactive Documentation
- **Swagger UI:** http://localhost:8080/docs (when running locally)
- **ReDoc:** http://localhost:8080/redoc (when running locally)

### Detailed Endpoints  
See [API_TESTING.md](API_TESTING.md) for:
- All 22 endpoints documented
- Example requests and responses
- Authentication details
- Error handling
- Test flows

---

## 🔐 Security & Secrets

**Where to read about:**
- Configuration: [CONFIGURATION.md](CONFIGURATION.md)
- Local secrets: [QUICKSTART.md](QUICKSTART.md) - Step 5
- Cloud secrets: [CLOUD_RUN_SETUP.md](CLOUD_RUN_SETUP.md) - Setup Cloud Run Secrets

**Key principles:**
- Never commit `.env` files (already in .gitignore)
- Use `.env.local.example` template for local development
- Use Google Secret Manager for production (Cloud Run)
- Same code works for both local and cloud!

---

## 📈 Performance & Monitoring

**Local monitoring:**
- View application logs in terminal

**Cloud monitoring:**
- View logs: `gcloud run logs read search-engine-api --follow`
- View metrics: Google Cloud Console > Cloud Run > search-engine-api
- Setup alerts: See [CLOUD_RUN_SETUP.md](CLOUD_RUN_SETUP.md)

---

## 🚀 Deployment Environments

### Local Development
- **Setup Time:** 5 minutes
- **Guide:** [QUICKSTART.md](QUICKSTART.md)
- **Configuration:** `.env` file from `.env.local.example`
- **Database:** Local PostgreSQL
- **Secrets:** .env file (gitignored)

### Cloud Run Production
- **Setup Time:** 30 minutes (one-time)
- **Guide:** [CLOUD_RUN_SETUP.md](CLOUD_RUN_SETUP.md)
- **Configuration:** Google Secret Manager
- **Database:** Google Cloud SQL
- **Secrets:** Secret Manager (automatic injection)
- **Deployment:** Automatic (GitHub Actions)

---

## 📞 Quick Links

| Need | File | Section |
|------|------|---------|
| API Key | [QUICKSTART.md](QUICKSTART.md) | Step 5 |
| Database Setup | [QUICKSTART.md](QUICKSTART.md) | Step 4 |
| First Test | [API_TESTING.md](API_TESTING.md) | Test 1 |
| Cloud Deploy | [CLOUD_RUN_SETUP.md](CLOUD_RUN_SETUP.md) | Initial Setup |
| Troubleshooting | [CONFIGURATION.md](CONFIGURATION.md) | Troubleshooting |
| System Arch | [SYSTEM_FLOW.md](SYSTEM_FLOW.md) | Overview |

---

## ✅ Verification Checklist

- [ ] Read [CLOUD_RUN_MIGRATION.md](CLOUD_RUN_MIGRATION.md) for overview
- [ ] Ran [QUICKSTART.md](QUICKSTART.md) for local setup
- [ ] Successfully ran `python main.py`
- [ ] Accessed http://localhost:8080/docs
- [ ] Tested at least one API endpoint
- [ ] Understood configuration from [CONFIGURATION.md](CONFIGURATION.md)
- [ ] Reviewed [CLOUD_RUN_SETUP.md](CLOUD_RUN_SETUP.md) for production

---

## 🎓 Learning Path

**Time: ~2 hours total**

1. **Project Overview** (10 min)
   - [README.md](README.md)
   - [CLOUD_RUN_MIGRATION.md](CLOUD_RUN_MIGRATION.md)

2. **Local Setup** (20 min)
   - [QUICKSTART.md](QUICKSTART.md)
   - Run application locally

3. **Configuration** (15 min)
   - [CONFIGURATION.md](CONFIGURATION.md)
   - Understand secrets management

4. **API Testing** (15 min)
   - [API_TESTING.md](API_TESTING.md)
   - Make sample API calls

5. **Architecture** (20 min)
   - [SYSTEM_FLOW.md](SYSTEM_FLOW.md)
   - [README_COMPLETE.md](README_COMPLETE.md)

6. **Cloud Deployment** (20 min)
   - [CLOUD_RUN_SETUP.md](CLOUD_RUN_SETUP.md)
   - Understand production setup

---

## 📞 Still Need Help?

1. **Read:** The specific documentation file listed above
2. **Search:** Use Ctrl+F to search within documentation files
3. **Check:** Troubleshooting sections in relevant documentation
4. **Review:** Code comments in source files
5. **Test:** Try the example API calls in [API_TESTING.md](API_TESTING.md)

---

**Last Updated:** 2024
**Status:** Production Ready ✅
**Documentation Level:** Comprehensive 📚
