# ChemAgent GCP Deployment Guide

This guide provides instructions on how to deploy the ChemAgent AI application to Google Cloud Platform using **Cloud Run** and optionally **Cloud SQL**. The application uses a unified architecture where the FastAPI backend serves the compiled React frontend, requiring only a single container to be deployed.

## 1. Prerequisites
- [Google Cloud SDK (gcloud)](https://cloud.google.com/sdk/docs/install) installed.
- A Google Cloud Project with billing enabled.
- Necessary APIs enabled:
  ```bash
  gcloud services enable run.googleapis.com \
                         cloudbuild.googleapis.com \
                         sqladmin.googleapis.com \
                         secretmanager.googleapis.com
  ```

## 2. Deploying to Cloud Run (Stateless / SQLite)

For a quick start, you can deploy using the integrated Dockerfile which uses the local SQLite database. Note that SQLite data is ephemeral on Cloud Run and will reset upon container restart.

```bash
# Build and deploy using Google Cloud Build
gcloud builds submit --config cloudbuild.yaml .
```

### Passing Secrets (Gemini API Key)
Ensure you set your API key in the Cloud Run service. You can do this securely via Secret Manager, or directly via environment variables:

```bash
gcloud run services update chemagent-service \
    --set-env-vars="GEMINI_API_KEY=your-api-key-here" \
    --region=us-central1
```

## 3. Persistent Storage with Cloud SQL (PostgreSQL)

To retain simulation history persistently, switch from SQLite to Cloud SQL.

### Step 3.1: Create a Cloud SQL Instance
```bash
gcloud sql instances create chemagent-db-instance \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1
```

### Step 3.2: Create the Database & User
```bash
gcloud sql databases create chemagentdb --instance=chemagent-db-instance
gcloud sql users create chemuser --instance=chemagent-db-instance --password=your_secure_password
```

### Step 3.3: Deploy with Cloud SQL Connections
Update your Cloud Run service to connect to the Cloud SQL instance using the Cloud SQL proxy.

```bash
# Get the connection name
INSTANCE_CONNECTION_NAME=$(gcloud sql instances describe chemagent-db-instance --format="value(connectionName)")

# Update Cloud Run
gcloud run services update chemagent-service \
    --add-cloudsql-instances=$INSTANCE_CONNECTION_NAME \
    --set-env-vars="DATABASE_URL=postgresql+asyncpg://chemuser:your_secure_password@/chemagentdb?host=/cloudsql/$INSTANCE_CONNECTION_NAME" \
    --region=us-central1
```

## 4. Continuous Integration / Deployment (CI/CD)
The project includes a `cloudbuild.yaml` file. You can connect your GitHub or Google Cloud Source Repositories to Cloud Build to automatically trigger deployments on every push to the `main` branch.
