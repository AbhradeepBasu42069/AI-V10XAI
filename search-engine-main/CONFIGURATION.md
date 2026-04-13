# Configuration & Secrets Management

## 🔄 Overview

CampusHire uses a **flexible configuration system** that adapts to different environments:
- **Local Development:** Reads from `.env` file
- **Cloud Run (Production):** Reads from Google Cloud Secret Manager (injected as environment variables)

---

## 📁 Configuration Files

### `.env.local.example` (USE THIS FOR LOCAL DEV)
**Purpose:** Template for local development configuration

**How to use:**
```bash
cp .env.local.example .env
# Edit .env with your local credentials
```

**Included in git?** ❌ No - `.env` is in `.gitignore` to prevent accidental secret commits

---

### `.env.example` (LEGACY)
**Status:** Older template file, kept for reference

**Recommendation:** Use `.env.local.example` instead (same content, clearer naming)

**Included in git?** ✅ Yes - because it has no real secrets

---

### `config.py` (THE ACTUAL CONFIGURATION)
**Purpose:** Centralized configuration management for the entire application

**How it works:**
```python
from dotenv import load_dotenv
import os

# Step 1: Try to load .env file (fails silently if not found)
load_dotenv()

# Step 2: Read environment variables
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),  # From .env OR environment
    'database': os.getenv('DB_NAME', 'campushire_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'port': os.getenv('DB_PORT', '5432')
}

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
MY_API_AUTH_KEY = os.getenv('MY_API_AUTH_KEY', 'fallback_dev_key')
```

**Why this works for both environments:**

| Environment | What Happens |
|-------------|--------------|
| **Local Development** | `load_dotenv()` reads from `.env` → `os.getenv()` accesses those vars |
| **Cloud Run** | `load_dotenv()` finds no `.env` (ignored) → `os.getenv()` reads Secret Manager values injected by GitHub Actions |

✅ **Key Point:** Same code works for both local AND cloud!

---

## 🚀 Local Development Setup (Recommended)

### Step 1: Create Local .env File

```bash
cp .env.local.example .env
```

### Step 2: Edit with Your Credentials

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=campushire_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password

GEMINI_API_KEY=your_gemini_key_from_google
MY_API_AUTH_KEY=local_dev_key_12345
```

### Step 3: Never Commit .env

```bash
# Already done! .env is in .gitignore
git status  # .env should NOT appear here
```

### Step 4: Run Application

```bash
python main.py
```

---

## ☁️ Cloud Run Deployment (Production)

### No .env File Needed!

In Cloud Run, secrets work like this:

```
GitHub Actions Workflow (deploy.yml)
    ↓
Google Cloud Secret Manager (GEMINI_API_KEY, MY_API_AUTH_KEY, DB_*)
    ↓
Cloud Run Service (environment variables injected automatically)
    ↓
config.py reads os.getenv() → gets Secret Manager values
```

### One-Time Setup

```bash
# Create secrets in Google Cloud
gcloud secrets create GEMINI_API_KEY --replication-policy="automatic"
echo "your_key" | gcloud secrets versions add GEMINI_API_KEY --data-file=-

gcloud secrets create MY_API_AUTH_KEY --replication-policy="automatic"
echo "your_key" | gcloud secrets versions add MY_API_AUTH_KEY --data-file=-

# (Same for DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)
```

### Automatic Deployment

```bash
git push origin main
# GitHub Actions automatically:
# 1. ✅ Builds Docker image
# 2. ✅ Pushes to Artifact Registry  
# 3. ✅ Deploys to Cloud Run
# 4. ✅ Injects secrets from Secret Manager
```

---

## 🔐 Security Best Practices

### ✅ DO

- ✅ Keep `config.py` in Git (it has no real secrets)
- ✅ Keep `.env.local.example` in Git (it's a template)
- ✅ Add actual `.env` files to `.gitignore` (already done)
- ✅ Use Cloud Secret Manager for production (never manual secrets)
- ✅ Never commit real API keys or passwords
- ✅ Rotate secrets regularly

### ❌ DON'T

- ❌ Don't commit `.env` files (already prevented by .gitignore)
- ❌ Don't paste real API keys in code
- ❌ Don't use .env files in production (use Secret Manager)
- ❌ Don't share production secrets in chat/email
- ❌ Don't check passwords into version control

---

## 🛠️ Troubleshooting

### Problem: "KeyError: GEMINI_API_KEY"

**Local Development:**
```bash
# Check if .env file exists
ls -la .env

# Check if it has the right key
grep GEMINI_API_KEY .env

# Restart Python application
python main.py
```

**Cloud Run:**
```bash
# Check if secret exists in Secret Manager
gcloud secrets list | grep GEMINI_API_KEY

# Verify service account can access it
gcloud secrets get-iam-policy GEMINI_API_KEY

# Check application logs
gcloud run logs read search-engine-api --follow
```

### Problem: "No such file or directory: '.env'"

**This is normal!** The application is designed to work without `.env` files (for Cloud Run).

**But for local development:**
```bash
# Create the .env file
cp .env.local.example .env
```

---

## 📊 Configuration Hierarchy

When the application starts, it looks for environment variables in this order:

```
1. Environment Variables (highest priority)
   ├─ Local: Read from .env file via load_dotenv()
   └─ Cloud: Read from Secret Manager (injected by Cloud Run)
   
2. Hardcoded Defaults (lowest priority)
   └─ DB_HOST defaults to 'localhost'
   └─ MIN_SIMILARITY_THRESHOLD defaults to 0.4
   └─ etc.
```

**Code Example:**
```python
# If MY_DB_HOST environment variable exists, use it
# Otherwise, use 'localhost' as fallback
DB_HOST = os.getenv('DB_HOST', 'localhost')
```

---

## 🚀 Quick Reference

| Task | Command |
|------|---------|
| **Local Dev Setup** | `cp .env.local.example .env` + edit values |
| **Check .env exists** | `ls -la .env` |
| **Run locally** | `python main.py` |
| **Deploy to Cloud** | `git push origin main` |
| **View Cloud secrets** | `gcloud secrets list` |
| **Update Cloud secret** | `echo "new_value" \| gcloud secrets versions add SECRET_NAME --data-file=-` |
| **View Cloud Run logs** | `gcloud run logs read search-engine-api --follow` |

---

## 📚 Related Documentation

- **Local Development:** See [QUICKSTART.md](QUICKSTART.md)
- **Production Deployment:** See [CLOUD_RUN_SETUP.md](CLOUD_RUN_SETUP.md)
- **API Reference:** Visit `http://localhost:8080/docs`

---

## ✅ Summary

| Aspect | Local | Cloud Run |
|--------|-------|-----------|
| **Config Source** | `.env` file | Secret Manager |
| **Secret Storage** | File (gitignored) | Google Cloud |
| **Deployment** | Manual (python main.py) | Automatic (git push) |
| **Security** | Dev/testing | Production-grade |
| **Code Changes** | None needed | Same code works! |

**Key Insight:** The same `config.py` code works for both environments because it uses environment variables, which are populated differently in each context. 🎯
