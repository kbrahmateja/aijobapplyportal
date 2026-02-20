#!/bin/bash

echo "🔄 Restarting AI Job Apply Portal Services..."

# 1. Kill existing services
echo "Stopping existing backend services..."
pkill -f "uvicorn.*main:app" || true

echo "Stopping existing frontend services..."
pkill -f "next dev" || true
pkill -f "next start" || true

# Wait a moment to ensure ports are freed
sleep 2

# 2. Start Backend
echo "🚀 Starting FastAPI Backend..."
cd apps/api
source .venv/bin/activate
set -a
source .env
set +a
nohup uvicorn main:app --reload --host 127.0.0.1 --port 8000 > backend.log 2>&1 &
cd ../..

# 3. Start Frontend
echo "🚀 Starting Next.js Frontend..."
cd apps/web
# Source zshrc to ensure npx/npm are in path if running from weird contexts
source ~/.zshrc 2>/dev/null || true
nohup npm run dev > frontend.log 2>&1 &
cd ../..

echo "✅ Services restarted successfully in the background!"
echo "   - Frontend is running on http://localhost:3000"
echo "   - Backend is running on http://127.0.0.1:8000"
echo "   (Logs are available in apps/api/backend.log and apps/web/frontend.log)"
