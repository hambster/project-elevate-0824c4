#!/usr/bin/env bash
# ==============================================================================
# Deploy hr-agent to Google Cloud Run
# ==============================================================================
set -euo pipefail

# Configuration defaults
PROJECT_ID="${GCP_PROJECT_ID:-project-elevate-0824c4}"
REGION="${GCP_REGION:-asia-east1}"
SERVICE_NAME="${SERVICE_NAME:-hr-agent}"
MEMORY="${MEMORY:-2Gi}"
CPU="${CPU:-1}"
CONCURRENCY="${CONCURRENCY:-8}"
MIN_INSTANCES="${MIN_INSTANCES:-0}"
MAX_INSTANCES="${MAX_INSTANCES:-10}"
PORT="${PORT:-8080}"
ALLOW_UNAUTHENTICATED="${ALLOW_UNAUTHENTICATED:-true}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

echo "============================================================"
echo " Deploying ${SERVICE_NAME} to Google Cloud Run"
echo "============================================================"
echo " Project ID            : ${PROJECT_ID}"
echo " Region                : ${REGION}"
echo " Service Name          : ${SERVICE_NAME}"
echo " Unauthenticated Access: ${ALLOW_UNAUTHENTICATED}"
echo " Memory / CPU          : ${MEMORY} / ${CPU} vCPU"
echo " Instances             : ${MIN_INSTANCES} (min) - ${MAX_INSTANCES} (max)"
echo " Source Directory      : ${SCRIPT_DIR}"
echo "============================================================"

# Verify gcloud is installed
if ! command -v gcloud &> /dev/null; then
  echo "Error: 'gcloud' CLI is not installed or not in PATH." >&2
  echo "Please install Google Cloud SDK: https://cloud.google.com/sdk/docs/install" >&2
  exit 1
fi

# Set active project
echo "==> Configuring gcloud project..."
gcloud config set project "${PROJECT_ID}" --quiet

# Enable necessary GCP APIs
echo "==> Ensuring required Google Cloud APIs are enabled..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  aiplatform.googleapis.com \
  --project="${PROJECT_ID}"

# Prepare environment variables
ENV_VARS=(
  "GOOGLE_GENAI_USE_VERTEXAI=true"
  "GOOGLE_CLOUD_PROJECT=${PROJECT_ID}"
  "GOOGLE_CLOUD_LOCATION=global"
  "MODEL_NAME=${MODEL_NAME:-gemini-3.6-flash}"
  "VERTEX_BASE_URL=https://aiplatform.googleapis.com"
  "MCP_TOKEN=${MCP_TOKEN:-mcp_olHWiuDEGP_tw5X_DU3eidmL9aS1pFJLDgFMySwmOqs}"
  "MOCK_SAAS_API_TOKEN=${MOCK_SAAS_API_TOKEN:-mcp_olHWiuDEGP_tw5X_DU3eidmL9aS1pFJLDgFMySwmOqs}"
  "X_MCP_TOKEN=${X_MCP_TOKEN:-mcp_olHWiuDEGP_tw5X_DU3eidmL9aS1pFJLDgFMySwmOqs}"
  "MOCK_SAAS_BASE_URL=${MOCK_SAAS_BASE_URL:-https://mock-saas.aishprabhat.demo.altostrat.com}"
  "WORKWEEK_MCP_URL=${WORKWEEK_MCP_URL:-https://mock-saas.aishprabhat.demo.altostrat.com/work-week/mcp/}"
  "SERVICEIMMEDIATELY_MCP_URL=${SERVICEIMMEDIATELY_MCP_URL:-https://mock-saas.aishprabhat.demo.altostrat.com/service-immediately/mcp/}"
  "DEFAULT_EMPLOYEE_ID=${DEFAULT_EMPLOYEE_ID:-EMP-486}"
  "DEFAULT_USER_EMAIL=${DEFAULT_USER_EMAIL:-waynelinn@google.com}"
)

# Join array elements with commas
ENV_VARS_STRING=$(IFS=,; echo "${ENV_VARS[*]}")

# Build auth flag
AUTH_FLAG="--no-allow-unauthenticated"
if [ "${ALLOW_UNAUTHENTICATED}" = "true" ]; then
  AUTH_FLAG="--allow-unauthenticated"
fi

echo "==> Deploying Cloud Run service from source with unauthenticated access enabled..."
gcloud run deploy "${SERVICE_NAME}" \
  --source . \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --platform=managed \
  ${AUTH_FLAG} \
  --quiet \
  --port="${PORT}" \
  --memory="${MEMORY}" \
  --cpu="${CPU}" \
  --concurrency="${CONCURRENCY}" \
  --min-instances="${MIN_INSTANCES}" \
  --max-instances="${MAX_INSTANCES}" \
  --set-env-vars="${ENV_VARS_STRING}"

# Explicitly ensure IAM policy allows unauthenticated invocations if requested
if [ "${ALLOW_UNAUTHENTICATED}" = "true" ]; then
  echo "==> Granting public invoker role (roles/run.invoker) to allUsers..."
  gcloud run services add-iam-policy-binding "${SERVICE_NAME}" \
    --project="${PROJECT_ID}" \
    --region="${REGION}" \
    --member="allUsers" \
    --role="roles/run.invoker" \
    --quiet
fi

echo ""
echo "============================================================"
echo " Deployment Complete!"
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --project="${PROJECT_ID}" --region="${REGION}" --format='value(status.url)')
echo " Service URL : ${SERVICE_URL}"
echo " Access      : Public (Unauthenticated)"
echo "============================================================"
