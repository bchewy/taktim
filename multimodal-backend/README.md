# Multimodal Backend with CrewAI

A powerful multimodal content analysis system using CrewAI agents for processing text, images, and documents.

## Features

- **Multimodal Analysis**: Process text documents, images, PDFs, Word docs, and spreadsheets
- **CrewAI Agents**: Specialized AI agents for different content types
- **Async Processing**: Background task processing for large files
- **Interactive Chat**: Chat with context from analyzed content
- **REST API**: Complete API for file uploads and analysis
- **Docker Support**: Containerized deployment

## API Endpoints

- `POST /api/upload` - Upload files (images, PDFs, docs)
- `POST /api/analyze` - Start content analysis with CrewAI agents
- `GET /api/results/{task_id}` - Get analysis results
- `POST /api/chat` - Interactive chat with multimodal context
- `GET /api/health` - Health check

## Quick Start

1. **Setup Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

2. **Run with Docker**:
   ```bash
   docker-compose up --build
   ```

3. **API Access**:
   - API: http://localhost:8001
   - Health: http://localhost:8001/api/health
   - Docs: http://localhost:8001/docs

## Usage Example

1. **Upload a file**:
   ```bash
   curl -X POST "http://localhost:8001/api/upload" \
        -H "Content-Type: multipart/form-data" \
        -F "file=@document.pdf"
   ```

2. **Start analysis**:
   ```bash
   curl -X POST "http://localhost:8001/api/analyze" \
        -H "Content-Type: application/json" \
        -d '{"query": "Summarize this document", "file_ids": ["file-id-here"]}'
   ```

3. **Get results**:
   ```bash
   curl "http://localhost:8001/api/results/task-id-here"
   ```

## Supported File Types

- **Images**: JPG, PNG, GIF, BMP, TIFF
- **Documents**: PDF, DOCX, DOC, TXT
- **Spreadsheets**: XLSX, XLS, CSV

## Architecture

- **Document Agent**: Analyzes text documents and extracts insights
- **Image Agent**: Processes images with OCR and visual analysis
- **Synthesizer Agent**: Combines insights from multiple sources
- **Chat Agent**: Interactive conversations with analysis context

## Environment Variables

- `OPENAI_API_KEY`: Required for AI processing
- `ANTHROPIC_API_KEY`: Optional for additional AI models
- `CREWAI_TELEMETRY_OPT_OUT`: Disable CrewAI telemetry

## Development

Mount source code for live reloading (already configured in docker-compose.yml):

```bash
docker-compose up --build
# Code changes will automatically reload the server
```