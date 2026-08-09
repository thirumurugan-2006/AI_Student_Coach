# AI Career Coach

A production-ready AI-powered career coach system using Groq LLM API for fast, cloud-based inference.

## Architecture

```
Frontend (Streamlit)
    ↓ HTTP/REST API
Backend (FastAPI)
    ↓
Career Coach Agent
    ↓
Skills (Survey, Assessment, Learning, Placement, Interview, Reflection)
    ↓
LLM Interface
    ↓
Groq Service
    ↓
Groq API (Llama 3 8B)
```

## Features

- **AI Career Discovery Survey**: Personalized career goal identification
- **Technical Skill Assessment**: Adaptive assessments with knowledge graph tracking
- **Learning Roadmap**: AI-generated personalized learning paths
- **Placement Simulation**: Comprehensive placement readiness assessment with visual analytics
- **Mock Interviews**: Realistic interview simulation with feedback
- **Reflection**: Confidence tracking and learning insights
- **Evaluation Engine**: Centralized progress and readiness scoring
- **SQLite Persistence**: Full database integration with SQLAlchemy
- **JWT Authentication**: Secure user authentication and authorization

## Tech Stack

### Backend
- **Framework**: FastAPI
- **LLM**: Groq API (Llama 3 8B)
- **Database**: SQLite with SQLAlchemy 2.0
- **Migrations**: Alembic
- **Authentication**: JWT with passlib
- **Async**: aiosqlite for async SQLite

### Frontend
- **Framework**: Streamlit
- **HTTP**: requests library
- **Visualization**: Plotly

## Setup Instructions

### Prerequisites

1. **Groq API Key**: Get a free API key from https://console.groq.com/keys

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   copy .env.example .env
   ```
   Edit `.env` with your configuration:
   ```env
   DATABASE_URL=sqlite+aiosqlite:///./data/career_coach.db
   SECRET_KEY=your-secret-key-here-change-in-production
   LLM_PROVIDER=groq
   GROQ_API_KEY=your-groq-api-key-here
   GROQ_MODEL=llama3-8b-8192
   ```

5. **Start the backend server**
   ```bash
   uvicorn main:app --reload --port 8001
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd demo  # Note: Will be renamed to frontend in production
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the frontend**
   ```bash
   streamlit run app.py
   ```

## API Endpoints

### Authentication
- `POST /user/signup` - Sign up or login user
- `GET /user/profile` - Get user profile
- `GET /user/session` - Get user session

### Career Coach
- `POST /survey/` - Submit career survey
- `POST /assessment/` - Submit assessment
- `POST /learning/` - Generate learning roadmap
- `POST /placement/assess` - Assess placement readiness
- `GET /placement/progress` - Get placement progress
- `POST /interview/` - Submit interview response
- `POST /reflection/` - Submit reflection
- `GET /dashboard/` - Get student dashboard

### Health
- `GET /health` - Health check endpoint

## Database Schema

- **users**: User authentication
- **students**: Student profiles
- **surveys**: Career survey data
- **assessments**: Technical assessments
- **learning_roadmaps**: Learning paths
- **placement_assessments**: Placement readiness data
- **interviews**: Interview sessions
- **reflections**: Reflection entries
- **progress**: Progress tracking
- **readiness_scores**: Industry readiness metrics

## Security

- JWT-based authentication
- Input validation with Pydantic
- CORS configuration
- SQL injection protection via SQLAlchemy
- Environment variable configuration for secrets

## Development

### Running Tests
```bash
# Backend
cd backend
pytest tests/

# Frontend
cd demo
streamlit run app.py
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Project Structure

```
.
├── backend/
│   ├── agent/           # AI Agent orchestration
│   ├── api/             # FastAPI routers
│   ├── auth/            # Authentication handlers
│   ├── config/          # Configuration
│   ├── core/            # Core utilities (LLM, logger, etc.)
│   ├── database/        # Database session
│   ├── evaluation/      # Evaluation engine
│   ├── memory/          # Student memory
│   ├── models/          # SQLAlchemy models
│   ├── placement/       # Placement simulation module
│   ├── repositories/    # Repository pattern
│   ├── services/        # Groq service
│   ├── skills/          # AI skills
│   ├── alembic/         # Database migrations
│   ├── main.py          # Application entry
│   └── requirements.txt
├── demo/               # Streamlit frontend (to be renamed to frontend)
│   ├── api/             # Frontend API clients
│   ├── components/      # UI components
│   ├── config/          # Frontend configuration
│   ├── state/           # Session state management
│   ├── utils/           # UI utilities
│   ├── app.py           # Frontend entry
│   └── requirements.txt
├── docs/               # Documentation
└── README.md
```

## License

MIT License
