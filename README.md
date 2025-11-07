# Prompt Enhancer

An intelligent web service for enhancing AI prompts using open-source NLP models and structured frameworks.

## Features

- **Multi-dimensional Quality Scoring**: Clarity, Specificity, Context Richness, Actionability
- **NLP-Powered Analysis**: spaCy for linguistic analysis, Transformers for semantic enhancement
- **Framework-Based Enhancement**: APE, STAGE, CLEAR frameworks with extensible JSON definitions
- **AI-Driven Improvement**: Local Hugging Face models (T5) for prompt refinement
- **No External APIs**: Fully self-contained using open-source models

## Quick Start

### Backend Setup
```bash
cd backend
# Using conda
conda env create -f environment.yml
conda activate prompt-enhancer
python setup_models.py  # Download NLP models
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or using pip
pip install -r requirements.txt
python setup_models.py
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup
```bash
cd frontend
python -m http.server 3000
```

### Access
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Architecture

### Core Components

1. **Analyzer** - Advanced NLP analysis using spaCy
   - Entity recognition
   - Dependency parsing
   - Complexity scoring
   - Linguistic feature extraction

2. **Synthesizer** - AI-enhanced prompt generation
   - Template filling
   - Hugging Face T5 integration
   - Text naturalization
   - Semantic improvement

3. **Evaluator** - Multi-dimensional quality assessment
   - Clarity scoring
   - Specificity metrics
   - Context richness analysis
   - Actionability evaluation

4. **Selector** - Framework recommendation engine
   - Rule-based matching
   - Intent classification
   - Domain-specific routing

### Enhancement Frameworks

- **APE**: Action, Purpose, Expectation
- **STAGE**: Situation, Task, Action, Goal, Expectation  
- **CLEAR**: Context, Length, Emotion, Audience, Role

## API Endpoints

- `GET /frameworks` - List available frameworks
- `POST /enhance` - Enhance a prompt
- `POST /auto` - Get framework suggestions
- `POST /frameworks/upload` - Upload new framework

## Dependencies

- FastAPI + Uvicorn
- spaCy (en_core_web_sm)
- Transformers (T5)
- PyTorch

## Development

The system is designed to be framework-agnostic and extensible. New enhancement frameworks can be added as JSON files without code changes.

For production deployment, consider:
- GPU acceleration for transformers
- Model caching strategies
- Rate limiting
- Authentication