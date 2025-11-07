# Prompt Enhancer - Docker Setup

## Quick Start with Docker

```bash
# Clone and navigate
cd prompt-enhancer

# Start both services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

## Environment Setup

1. Copy your Gemini API key to `.env`:
```bash
GEMINI_API_KEY=your_api_key_here
```

## Services

- **Backend**: FastAPI server on port 8000
- **Frontend**: Nginx server on port 3000

## Development

```bash
# Rebuild after changes
docker-compose up --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```