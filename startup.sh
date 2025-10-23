#!/bin/bash
set -e

# Handle GCloud service account credentials if provided
if [ -n "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
  echo "🔐 Service account credentials found"
  if [ -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "✅ Using service account from file"
  else
    echo "⚠️  Service account file not found, but environment variable is set"
  fi
fi

# Handle JSON credentials from environment variable (check multiple possible names)
if [ -n "$GOOGLE_APPLICATION_CREDENTIALS_JSON" ]; then
  echo "🔐 Service account JSON found in environment (GOOGLE_APPLICATION_CREDENTIALS_JSON)"
  echo "$GOOGLE_APPLICATION_CREDENTIALS_JSON" > /tmp/service-account.json
  export GOOGLE_APPLICATION_CREDENTIALS=/tmp/service-account.json
  chmod 600 /tmp/service-account.json
elif [ -n "$GOOGLE_SERVICE_ACCOUNT_JSON" ]; then
  echo "🔐 Service account JSON found in environment (GOOGLE_SERVICE_ACCOUNT_JSON)"
  echo "$GOOGLE_SERVICE_ACCOUNT_JSON" > /tmp/service-account.json
  export GOOGLE_APPLICATION_CREDENTIALS=/tmp/service-account.json
  chmod 600 /tmp/service-account.json
fi

# Start the FastAPI application
echo "🚀 Starting FastAPI application"
exec uvicorn main:app \
  --host 0.0.0.0 \
  --port ${PORT:-8080} \
  --workers 1 \
  --log-level info

