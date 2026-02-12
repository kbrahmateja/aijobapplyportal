# AI Job Apply Portal

An intelligent job application automation system powered by AI agents.

## 🚀 Features

- **Job Discovery**: Scrape jobs from multiple sources (LinkedIn, WeWorkRemotely, Indeed)
- **AI-Powered Matching**: Intelligent job-resume matching using embeddings and LangChain
- **Modern Job Portal**: Beautiful Next.js frontend with advanced search, filters, and pagination
- **Automated Applications**: AI agents handle job applications with customized cover letters
- **Resume Intelligence**: Parse and analyze resumes using AI
- **User Authentication**: Secure authentication via Clerk
- **Real-time Dashboard**: Track application status and job matches

## 📦 Architecture

```
aijobapplyportal/
├── apps/
│   ├── api/          # FastAPI backend
│   └── web/          # Next.js frontend
└── docker-compose.yml
```

### Backend (FastAPI)
- **Framework**: FastAPI 0.109+
- **Database**: PostgreSQL with pgvector for embeddings
- **AI Stack**: LangChain, LangGraph, OpenAI, Anthropic
- **Background Jobs**: Celery + Redis
- **Web Scraping**: Playwright
- **Authentication**: JWT tokens (Clerk integration)

### Frontend (Next.js)
- **Framework**: Next.js 16.1.6 with React 19
- **Styling**: Tailwind CSS 4.0
- **UI Components**: Radix UI, shadcn/ui
- **Authentication**: Clerk
- **Icons**: Lucide React

## 🛠️ Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+

### Backend Setup

```bash
cd apps/api

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials:
# - DATABASE_URL
# - OPENAI_API_KEY
# - CLERK_SECRET_KEY
# - REDIS_URL

# Run migrations
alembic upgrade head

# Start API server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Start Celery workers (in separate terminals)
celery -A worker worker --loglevel=info
celery -A worker worker --loglevel=info  # Additional worker for parallel processing
```

### Frontend Setup

```bash
cd apps/web

# Install dependencies
npm install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local with:
# - NEXT_PUBLIC_API_URL=http://localhost:8000
# - NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
# - CLERK_SECRET_KEY

# Start development server
npm run dev
```

### Database Setup

```bash
# Start PostgreSQL with pgvector extension
docker-compose up -d postgres

# Or install locally and enable pgvector:
psql -U postgres
CREATE DATABASE aijobapply;
\c aijobapply
CREATE EXTENSION vector;
```

## 🎯 Usage

1. **Sign Up/Sign In**: Create an account via Clerk authentication
2. **Upload Resume**: Go to Profile page and upload your PDF resume
3. **Browse Jobs**: Visit the Jobs page to see scraped opportunities
4. **Filter & Search**: Use advanced filters (category, location, source) and search
5. **View Matches**: AI analyzes your resume and shows compatibility scores
6. **Apply with AI**: Click "Apply w/ AI" to let the agent handle the application

## 🔧 Configuration

### Environment Variables

#### Backend (`apps/api/.env`)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/aijobapply
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
CLERK_SECRET_KEY=sk_live_...
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

#### Frontend (`apps/web/.env.local`)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...
CLERK_SECRET_KEY=sk_live_...
```

## 📊 Features Detail

### Job Portal UX
- ✅ **Sticky Header & Sidebar**: Search and filters stay visible while scrolling
- ✅ **Grid/List View Toggle**: Switch between compact cards and detailed rows
- ✅ **Advanced Pagination**: Navigate through large job datasets efficiently
- ✅ **Smart Filtering**: Category, location, and source filters with auto-reset
- ✅ **Auto-scroll**: Results automatically scroll to top when filters change
- ✅ **Responsive Design**: Mobile-first, works on all screen sizes

### AI Agents
- **Job Discovery Agent**: Scrapes jobs from multiple platforms
- **Resume Intelligence Agent**: Parses and extracts structured data from PDFs
- **Job Matching Agent**: Computes similarity scores using embeddings
- **Application Execution Agent**: Fills forms and submits applications
- **Application Decision Agent**: Determines tier-based application strategy

## 🧪 Testing

```bash
# Backend tests
cd apps/api
pytest

# Frontend types check
cd apps/web
npm run build  # Includes TypeScript type checking
```

## 🚀 Production Build

```bash
# Build frontend
cd apps/web
npm run build
npm start

# Run backend with gunicorn
cd apps/api
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📝 Version

**Current Version**: 1.0.0

### Changelog

#### v1.0.0 (2026-02-12)
- ✅ Complete job portal with modern UX
- ✅ AI-powered job matching
- ✅ Multi-source job scraping
- ✅ Resume parsing and intelligence
- ✅ Clerk authentication integration
- ✅ Fixed pagination state management
- ✅ Fixed auto-scroll for filter changes
- ✅ TypeScript build errors resolved

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with FastAPI, Next.js, LangChain, and Playwright
- UI components from shadcn/ui
- Authentication by Clerk
- AI models from OpenAI and Anthropic
