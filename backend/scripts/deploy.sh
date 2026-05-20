#!/bin/bash
set -euo pipefail

echo "=== FORGE API Deployment ==="

echo "1. Running migrations..."
alembic upgrade head

echo "2. Deploying to Fly.io..."
fly deploy --ha=false

echo "3. Checking health..."
sleep 5
curl -sf https://forge-api.fly.dev/health || { echo "Health check failed!"; exit 1; }
curl -sf https://forge-api.fly.dev/health/ready || { echo "Readiness check failed!"; exit 1; }

echo ""
echo "=== Deployment complete ==="
