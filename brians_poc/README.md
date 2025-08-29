# GeoGov Lite - Compliance Analysis System

A simplified compliance analysis system using AI-powered document retrieval and analysis to determine if software features require geographical compliance.

## 🚀 Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- OpenAI API key (required)
- Exa API key (optional, for enhanced search)
- Perplexity API key (optional, for enhanced search)

### 1. Setup Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
OPENAI_API_KEY=your_openai_api_key_here
EXA_API_KEY=your_exa_api_key_here  # optional
PERPLEXITY_API_KEY=your_perplexity_api_key_here  # optional
```

### 2. Run the Application
```bash
# Start both frontend and backend
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### 3. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🏗️ Architecture

### Simplified Stack
- **Frontend**: React + Vite + Nginx (Port 3000)
- **Backend**: FastAPI + Python (Port 8000)
- **Vector Store**: Chroma (local, persistent)
- **Database**: SQLite (local, persistent)
- **LLM**: OpenAI GPT-4o-mini

### Data Flow
```
Search APIs → Document Scraping → Chroma Vector Store → RAG Analysis → SQLite Storage
```

## 📊 Key Features

### Compliance Analysis
- **Three-stage analysis**: Finder → Counter → Judge
- **RAG-powered**: Retrieves relevant legal documents
- **Dual decision modes**: LLM-based vs Rules-based
- **Persistent storage**: SQLite database for analysis history

### Document Sources
- **Perplexity API**: Real-time search of legal documents
- **Exa API**: AI-powered search for official government sources
- **Auto-scraping**: Full document content extraction
- **Official domains**: Focus on .gov, .eu, and legal databases

## 🔧 Configuration

### Environment Variables
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | ✅ | - | OpenAI API key for LLM analysis |
| `EXA_API_KEY` | ❌ | - | Exa API key for enhanced search |
| `PERPLEXITY_API_KEY` | ❌ | - | Perplexity API key for search |
| `USE_RAG` | ❌ | `true` | Enable RAG analysis |
| `USE_RULES_ENGINE` | ❌ | `false` | Use rules vs LLM for decisions |
| `RAG_TOPK` | ❌ | `6` | Number of documents to retrieve |

### Configuration Files
- **`backend/inputs.yaml`**: Define regulations and test features
- **`backend/rules.yaml`**: Rules engine configuration

## 📋 API Endpoints

### Core Analysis
- `POST /api/analyze` - Analyze single feature
- `POST /api/bulk_analyze` - Analyze multiple features
- `GET /api/evidence` - Download evidence ZIP

### System Management  
- `GET /api/health` - System health check
- `GET /api/rag_status` - RAG system status
- `POST /api/refresh_corpus` - Update knowledge base
- `POST /api/toggle_rag` - Enable/disable RAG

## 🗄️ Data Storage

### Vector Store (Chroma)
- **Location**: `data/chroma_db/`
- **Purpose**: Legal document embeddings
- **Persistent**: Yes, mounted in Docker

### Database (SQLite)
- **Location**: `data/analysis.db`
- **Tables**: `analyses`, `documents`
- **Purpose**: Analysis history and metadata

## 🛠️ Development

### Local Development
```bash
# Backend only
cd backend
pip install -r requirements.txt
python main.py

# Frontend only  
cd frontend
npm install
npm run dev
```

### Adding Regulations
Edit `backend/inputs.yaml`:
```yaml
regulations:
  - name: "Your Regulation Name"
    jurisdiction: "Your Jurisdiction"
```

### Custom Rules
Edit `backend/rules.yaml`:
```yaml
rules:
  - id: "your_rule"
    verdict: true
    reason: "Your reason"
    regulations: ["Regulation Name"]
    when_any_text: ["keyword1", "keyword2"]
```

## 🔍 Sample Analysis

The system includes sample test features:
1. **Personalized Content Feed** - Expected: Compliance Required (EU DSA)
2. **Basic Chat Messaging** - Expected: No Compliance Needed
3. **Youth-Targeted Ads** - Expected: Compliance Required (COPPA, SB976)

## 🚨 Troubleshooting

### Common Issues
1. **"No search clients available"** - Add API keys to `.env`
2. **"RAG initialization failed"** - Check OpenAI API key
3. **"No regulations configured"** - Ensure `inputs.yaml` exists
4. **Frontend can't reach API** - Check Docker networking

### Health Checks
```bash
# Check backend health
curl http://localhost:8000/api/health

# Check RAG status
curl http://localhost:8000/api/rag_status

# Check frontend
curl http://localhost:3000
```

### Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend
```

## 📝 License

This project is for compliance analysis and research purposes.