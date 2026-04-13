# Cloud Run Deployment Guide

Complete setup guide for deploying CampusHire to **Google Cloud Run** with **Secret Manager** and **GitHub Actions**.

---

## 🏗️ Architecture Overview

```
┌─────────────────┐
│  GitHub Repo    │
│   (Main Push)   │
└────────┬────────┘
         │
         ├─→ GitHub Actions (deploy.yml)
         │   ├─ Authenticate via Workload Identity
         │   ├─ Build Docker image
         │   └─ Push to Artifact Registry
         │
         ├─→ Cloud Build
         │
         └─→ Cloud Run (search-engine-api)
             ├─ Reads secrets from Secret Manager
             ├─ Connects to Cloud SQL (PostgreSQL)
             └─ Serves API on https://search-engine-api-...asia-south1.a.run.app
```

---

## 🔐 Initial Setup (One-Time)

### 1. Create Google Cloud Secrets

```bash
# Set project
gcloud config set project campus-hire-485321

# Create all required secrets
gcloud secrets create GEMINI_API_KEY --replication-policy="automatic"
echo "YOUR_GEMINI_API_KEY" | gcloud secrets versions add GEMINI_API_KEY --data-file=-

gcloud secrets create MY_API_AUTH_KEY --replication-policy="automatic"
echo "YOUR_API_AUTH_KEY" | gcloud secrets versions add MY_API_AUTH_KEY --data-file=-

gcloud secrets create DB_HOST --replication-policy="automatic"
echo "your-cloud-sql-public-ip" | gcloud secrets versions add DB_HOST --data-file=-

gcloud secrets create DB_PORT --replication-policy="automatic"
echo "5432" | gcloud secrets versions add DB_PORT --data-file=-

gcloud secrets create DB_NAME --replication-policy="automatic"
echo "campushire_db" | gcloud secrets versions add DB_NAME --data-file=-

gcloud secrets create DB_USER --replication-policy="automatic"
echo "postgres" | gcloud secrets versions add DB_USER --data-file=-

gcloud secrets create DB_PASSWORD --replication-policy="automatic"
echo "YOUR_DB_PASSWORD" | gcloud secrets versions add DB_PASSWORD --data-file=-
```

### 2. Grant Cloud Run Service Account Access to Secrets

```bash
# Get the Cloud Run service account
export SA_EMAIL=$(gcloud iam service-accounts list --filter="email:*cloudrun" --format='value(email)' --project=campus-hire-485321)

# Grant secretAccessor role for each secret
for secret in GEMINI_API_KEY MY_API_AUTH_KEY DB_HOST DB_PORT DB_NAME DB_USER DB_PASSWORD; do
  gcloud secrets add-iam-policy-binding $secret \
    --member=serviceAccount:$SA_EMAIL \
    --role=roles/secretmanager.secretAccessor
done
```

### 3. Verify Workload Identity Configuration

Your GitHub Actions workflow already uses Workload Identity:

```bash
# Verify the Workload Identity Provider exists
gcloud iam workload-identity-pools providers list --location=global --workload-identity-pool=github

# Should output something like:
# DISPLAY_NAME: GitHub
# LOCATION: global
# NAME: projects/{PROJECT_ID}/locations/global/workloadIdentityPools/github/providers/github-provider
```

---

## 📝 GitHub Actions Workflow (deploy.yml)

Your existing `deploy.yml` should look like this:

```yaml
name: Deploy to Cloud Run
on:
  push:
    branches:
      - main

env:
  PROJECT_ID: campus-hire-485321
  REGION: asia-south1
  IMAGE_NAME: search-engine-api
  SERVICE_NAME: search-engine-api
  ARTIFACT_REPO: cloud-run-source-deploy

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    permissions:
      contents: read
      id-token: write
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: projects/${{ secrets.GCP_PROJECT_ID }}/locations/global/workloadIdentityPools/github/providers/github-provider
          service_account: github-actions@${{ env.PROJECT_ID }}.iam.gserviceaccount.com
      
      - uses: google-github-actions/setup-gcloud@v2
      
      - name: Build and Push Docker Image
        run: |
          gcloud builds submit \
            --tag "${{ env.REGION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/${{ env.ARTIFACT_REPO }}/${{ env.IMAGE_NAME }}" \
            --project=${{ env.PROJECT_ID }}
      
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy ${{ env.SERVICE_NAME }} \
            --image "${{ env.REGION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/${{ env.ARTIFACT_REPO }}/${{ env.IMAGE_NAME }}" \
            --region ${{ env.REGION }} \
            --platform managed \
            --allow-unauthenticated \
            --memory 1Gi \
            --cpu 1 \
            --timeout 60 \
            --max-instances 100 \
            --set-secrets GEMINI_API_KEY=GEMINI_API_KEY:latest \
            --set-secrets MY_API_AUTH_KEY=MY_API_AUTH_KEY:latest \
            --set-secrets DB_HOST=DB_HOST:latest \
            --set-secrets DB_PORT=DB_PORT:latest \
            --set-secrets DB_NAME=DB_NAME:latest \
            --set-secrets DB_USER=DB_USER:latest \
            --set-secrets DB_PASSWORD=DB_PASSWORD:latest
```

---

## 🐳 Docker Configuration

Your `Dockerfile` should be:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health').read()"

# Run application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

---

## ✅ Verification Steps

### 1. Check Cloud Run Service Status

```bash
gcloud run services describe search-engine-api --region asia-south1
```

Expected output shows:
- Status: OK ✅
- Service URL
- Latest Revision

### 2. Check Secret Manager Access

```bash
# Verify secrets exist
gcloud secrets list

# Verify service account has access
gcloud secrets get-iam-policy GEMINI_API_KEY
```

### 3. View Cloud Run Logs

```bash
# Real-time logs
gcloud run logs read search-engine-api --region asia-south1 --follow

# Last 50 lines
gcloud run logs read search-engine-api --region asia-south1 --limit 50
```

### 4. Test API Health Check

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe search-engine-api --region asia-south1 --format='value(status.url)')

# Test health endpoint
curl -X GET "$SERVICE_URL/health"

# Should return: {"status": "healthy"}
```

### 5. Test API with Authentication

```bash
SERVICE_URL=$(gcloud run services describe search-engine-api --region asia-south1 --format='value(status.url)')

# Get API key from secrets
API_KEY=$(gcloud secrets versions access latest --secret=MY_API_AUTH_KEY)

# Test API endpoint
curl -X GET "$SERVICE_URL/docs" \
  -H "X-API-Key: $API_KEY"
```

---

## 🚀 Deployment Process

### Automatic Deployment (Recommended)

1. **Make code changes locally**
2. **Commit to Git:**
   ```bash
   git add .
   git commit -m "Update feature"
   ```
3. **Push to main branch:**
   ```bash
   git push origin main
   ```
4. **GitHub Actions automatically:**
   - ✅ Builds Docker image
   - ✅ Pushes to Artifact Registry
   - ✅ Deploys to Cloud Run
   - ✅ Injects secrets automatically

### Manual Deployment (If Needed)

```bash
# Build image
gcloud builds submit \
  --tag "asia-south1-docker.pkg.dev/campus-hire-485321/cloud-run-source-deploy/search-engine-api"

# Deploy to Cloud Run
gcloud run deploy search-engine-api \
  --image "asia-south1-docker.pkg.dev/campus-hire-485321/cloud-run-source-deploy/search-engine-api" \
  --region asia-south1 \
  --set-secrets GEMINI_API_KEY=GEMINI_API_KEY:latest \
  --set-secrets MY_API_AUTH_KEY=MY_API_AUTH_KEY:latest \
  --set-secrets DB_HOST=DB_HOST:latest \
  --set-secrets DB_PORT=DB_PORT:latest \
  --set-secrets DB_NAME=DB_NAME:latest \
  --set-secrets DB_USER=DB_USER:latest \
  --set-secrets DB_PASSWORD=DB_PASSWORD:latest
```

---

## 🔄 Rollback Procedure

If a deployment has issues, rollback to previous version:

```bash
# List recent revisions
gcloud run revisions list --service=search-engine-api --region=asia-south1

# Deploy specific revision
gcloud run deploy search-engine-api \
  --region=asia-south1 \
  --revision=PREVIOUS_REVISION_NAME
```

---

## 📊 Monitoring

### View Service Metrics

```bash
# Open Cloud Console
gcloud run services describe search-engine-api --region asia-south1 --format='value(status.url)'

# Then navigate to the service in Google Cloud Console
# Monitor:
# - Request count
# - Error rate
# - Latency
# - Memory usage
```

### Set Up Alerts

```bash
# Create alert for error rate > 5%
gcloud alpha monitoring policies create \
  --notification-channels=[CHANNEL_ID] \
  --display-name="Cloud Run Error Rate Alert" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=5 \
  --condition-threshold-comparator=COMPARISON_GT
```

---

## 🔐 Security Checklist

- ✅ Workload Identity Federation enabled (no service account keys)
- ✅ Secrets stored in Secret Manager (not in code)
- ✅ Cloud Run service account has minimal permissions
- ✅ API protected with `X-API-Key` header
- ✅ Database connection over SSL/TLS
- ✅ GitHub Actions uses Workload Identity (no long-lived credentials)
- ✅ `.env` files in `.gitignore` (never committed)

---

## 🆘 Troubleshooting

### Issue: "Secret not found" Error

```
gcloud.gax.rpc._BaseServiceException: 403 Forbidden: Permission 'secretmanager.versions.access'
```

**Solution:**
```bash
# Verify service account has access
gcloud secrets get-iam-policy GEMINI_API_KEY
# Should show: roles/secretmanager.secretAccessor for your service account

# If not, grant access:
gcloud secrets add-iam-policy-binding GEMINI_API_KEY \
  --member=serviceAccount:your-service-account@campus-hire-485321.iam.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

### Issue: "Database Connection Refused"

**Solution:**
1. Verify Cloud SQL public IP in secret: `gcloud secrets versions access latest --secret=DB_HOST`
2. Check Cloud SQL instance is running: `gcloud sql instances describe campushire-db`
3. Verify firewall allows Cloud Run: Check Cloud SQL connections tab
4. Test connection locally: `psql -h <IP> -U postgres -d campushire_db`

### Issue: Deployment Timeout

**Solution:**
```bash
# Check Cloud Build logs
gcloud builds log [BUILD_ID]

# Increase timeout
gcloud run deploy search-engine-api \
  --timeout=300 \  # Increase from default 60s
  --region asia-south1
```

### Issue: Application Crashes on Startup

**Solution:**
```bash
# Check logs
gcloud run logs read search-engine-api --follow

# Common issues:
# 1. Database not initialized - run migrations
# 2. Missing environment variables - check secret mapping
# 3. Wrong credentials - verify secrets in Secret Manager
# 4. Port not 8080 - ensure main.py runs on port 8080
```

---

## 📞 Getting Service URL

```bash
gcloud run services describe search-engine-api --region asia-south1 --format='value(status.url)'

# Example output: https://search-engine-api-abc123-asia-south1.a.run.app
```

---

## 🔄 Update Secrets

To update a secret for your Cloud Run service:

```bash
# Update secret value
echo "new_value" | gcloud secrets versions add SECRET_NAME --data-file=-

# Redeploy to use new secret
gcloud run deploy search-engine-api \
  --region asia-south1 \
  --no-gen2  # Use Cloud Run (second generation)
```

---

## 📚 Useful Commands

```bash
# View all secrets
gcloud secrets list

# View secret value (CAREFUL!)
gcloud secrets versions access latest --secret=GEMINI_API_KEY

# View service URL
gcloud run services describe search-engine-api --region asia-south1 --format='value(status.url)'

# View recent deployments
gcloud run revisions list --service=search-engine-api --region=asia-south1

# View service logs
gcloud run logs read search-engine-api --region asia-south1 --follow

# Delete service (if needed)
gcloud run services delete search-engine-api --region asia-south1
```

---

## ✅ Checklist for First Deployment

- [ ] All secrets created in Secret Manager
- [ ] Service account has secretAccessor role
- [ ] Workload Identity Provider configured
- [ ] GitHub Actions workflow in place
- [ ] Dockerfile exists
- [ ] requirements.txt updated
- [ ] Code pushed to main branch
- [ ] GitHub Actions completed successfully
- [ ] Cloud Run service deployed and healthy
- [ ] Health endpoint returns 200 OK
- [ ] API endpoints accessible with auth header
- [ ] Logs show no errors

---

**Ready to deploy!** Push to `main` and watch your GitHub Actions workflow automatically deploy to Cloud Run. 🚀
