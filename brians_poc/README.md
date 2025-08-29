# GeoGov Lite - Enhanced Legal Compliance Analysis

A FastAPI-based system for automated geo-regulatory compliance analysis with integrated Perplexity and Exa.ai research capabilities.

## 🚀 New Features

- **Integrated Research APIs** - Perplexity and Exa.ai for real-time legal source discovery
- **Dynamic Input Configuration** - YAML-based regulation and feature definitions
- **Enhanced Knowledge Base** - Automatic research and indexing of official legal sources
- **Comprehensive Analysis Pipeline** - End-to-end compliance assessment with validation
- **Evidence Generation** - Complete audit trails with cryptographic receipts
- **Batch Processing** - Analyze multiple features with summary reporting

## Quick Start

### 1. Setup Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Configure API keys in .env
cp .env.example .env
# Edit .env with your API keys (see Configuration section below)
```

### 2. Run Analysis
```bash
# Full analysis with dynamic inputs
python3 run_analysis.py

# Single feature analysis
python3 run_analysis.py --feature F-2381

# Integration tests
python3 test_integration.py
```

### 3. Start API Server
```bash
# Start FastAPI server
uvicorn main:app --reload

# Test endpoints
curl -X POST http://localhost:8000/api/refresh_corpus
curl -X GET http://localhost:8000/api/health
```

The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

## 📁 Key Files

### Core System
- **`main.py`** - Enhanced FastAPI application with integrated scraping
- **`perplexity.py`** - Perplexity API client for legal research
- **`exa.py`** - Exa.ai API client (HTTP version)
- **`exa_sdk.py`** - Exa.ai official SDK client (recommended)

### Configuration & Input
- **`inputs.yaml`** - Dynamic configuration for regulations and test features
- **`rules.yaml`** - Compliance rules engine configuration
- **`.env`** - API keys and environment settings

### Analysis & Testing
- **`run_analysis.py`** - Complete analysis workflow runner
- **`test_integration.py`** - Integration tests for the enhanced system

## 🔧 Configuration

### API Keys Required
```env
# Core APIs
OPENAI_API_KEY=sk-...           # For LLM operations and Mem0
ANTHROPIC_API_KEY=sk-ant-...    # Alternative LLM (optional)

# Research APIs  
PERPLEXITY_API_KEY=pplx-...     # Perplexity search
EXA_API_KEY=...                 # Exa.ai search

# Optional
FIRECRAWL_API_KEY=fc-...        # Web scraping (future)
MEM0_KEY=m0-...                 # Mem0 cloud service
```

### Input Configuration (`inputs.yaml`)

The system now uses a dynamic YAML configuration file that defines:

#### Regulations to Research
```yaml
regulations:
  - name: "EU Digital Services Act"
    jurisdiction: "EU"
    topics: ["recommender_systems", "content_moderation"] 
    priority: "high"
```

#### Test Features
```yaml
test_features:
  - feature_id: "F-2381"
    title: "Personalized Home Feed v3"
    description: "Reranks videos using watch history; EU rollout planned."
    code_hints:
      - "uses ageGate() for minor detection"
      - "if region in ['EU','EEA']: apply_dsa_compliance()"
    tags: ["recommender", "personalization", "geo_eu"]
    expected_compliance: true
    expected_regulations: ["EU-DSA"]
```

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Analyze Single Feature
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d @sample_artifact.json
```

### Bulk Analysis
```bash
curl -X POST http://localhost:8000/api/bulk_analyze \
  -H "Content-Type: application/json" \
  -d '{"items": [<array_of_feature_artifacts>]}'
```

### Get Evidence ZIP
```bash
curl http://localhost:8000/api/evidence -o evidence.zip
```

### Refresh Corpus (Admin)
```bash
curl -X POST http://localhost:8000/api/refresh_corpus
```

## Sample Request

The `sample_artifact.json` file contains an example feature artifact:

```json
{
  "feature_id": "F-2381",
  "title": "Personalized Home Feed v3",
  "description": "Reranks videos using watch history; EU rollout planned.",
  "docs": ["https://internal/prd", "https://internal/trd"],
  "code_hints": ["uses ageGate()", "if region in ['EU','EEA']:"],
  "tags": ["recommender", "personalization", "minors_possible"]
}
```

## Configuration

The rules engine uses `rules.yaml` to define compliance requirements. The file includes starter rules for:

- EU DSA recommender systems
- EU DSA moderation appeals
- US state minor protection laws
- NCMEC reporting requirements
- Business geofencing detection

## Architecture

The application is structured as a single Python file (`main.py`) containing:

- **FastAPI endpoints** for all API routes
- **Pydantic models** for request/response validation
- **Rules engine** with YAML-based policy configuration
- **Signal extraction** using regex patterns and NER
- **Mock LLM integration** (replaceable with actual OpenAI/Anthropic calls)
- **RAG system** using BM25 and vector search
- **Evidence system** for audit trails and compliance reporting

## Simple, Effective RAG System

The application uses a **self-contained RAG implementation** that requires no external services or API keys:

### Why This Approach?

- ✅ **Zero dependencies** on external vector databases or embedding APIs
- ✅ **Fast startup** - no model downloads or API connections needed
- ✅ **Reliable operation** - works consistently across all environments
- ✅ **TF-IDF + Cosine Similarity** - proven, effective for document retrieval
- ✅ **No API keys required** - completely self-contained

### How It Works

1. **TF-IDF Vectorization**: Documents are converted to vectors using term frequency-inverse document frequency
2. **Cosine Similarity**: Query vectors are matched against document vectors
3. **Relevance Ranking**: Returns the most similar documents above a threshold
4. **Citation Generation**: Provides source attribution for retrieved content

### Extending to Mem0 (Optional)

If you prefer Mem0's advanced features, you can:
1. Install additional dependencies: `pip install mem0ai chromadb`
2. Replace the `RAGSystem` class with the Mem0 implementation
3. Configure your preferred vector store and embedding provider

## Production Considerations

This is a hackathon/demo implementation with simplified components:

- LLM calls are mocked (replace with actual API calls)
- Mem0 RAG system implemented but may need environment-specific tuning
- SQLite storage (upgrade to PostgreSQL for production)
- No authentication or RBAC
- Basic error handling

For production deployment, implement proper:
- LLM API integration with retry logic
- Vector database optimization (Pinecone, Weaviate, or properly configured Mem0)
- Authentication and authorization
- Rate limiting and monitoring
- Comprehensive error handling
- Horizontal scaling capabilities
