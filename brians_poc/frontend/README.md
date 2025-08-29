# GeoGov Frontend

React frontend for the GeoGov Lite compliance analysis system.

## Features

- **Feature Analysis Form**: Submit software features for LangChain RAG-powered compliance analysis
- **Real-time Results**: View detailed compliance decisions with confidence scores
- **System Status**: Monitor backend health and knowledge base status
- **Corpus Management**: Refresh legal document corpus
- **Evidence Export**: Download analysis evidence and receipts

## Setup

### Prerequisites

- Node.js 18+ 
- npm or yarn
- GeoGov backend running on port 8000

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Production Build

```bash
npm run build
npm run preview
```

## Architecture

### Components

- **App.jsx**: Main application component with state management
- **AnalysisForm.jsx**: Form for inputting feature details
- **ResultDisplay.jsx**: Displays compliance analysis results
- **SystemStatus.jsx**: Shows backend system health

### API Client

- **client.js**: Axios-based API client for backend communication
- Handles all REST API calls to the FastAPI backend
- Includes file download functionality for evidence

## Backend Integration

The frontend integrates with the GeoGov FastAPI backend endpoints:

- `POST /api/analyze` - Single feature analysis
- `POST /api/bulk_analyze` - Bulk feature analysis
- `GET /api/health` - System health check
- `POST /api/refresh_corpus` - Refresh legal document corpus
- `GET /api/evidence` - Download evidence ZIP

## LangChain RAG Features

The frontend showcases the LangChain RAG capabilities:

1. **Smart Legal Search**: Uses vector similarity to find relevant regulations
2. **AI-Powered Analysis**: GPT-5 analyzes features against legal context
3. **Evidence-Based Decisions**: Shows legal citations and confidence scores
4. **Real-time Processing**: Live updates during analysis

## Development

The frontend is built with:

- **React 18**: Component-based UI framework
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Beautiful icon library
- **Axios**: HTTP client for API calls

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_BASE_URL=http://localhost:8000
```