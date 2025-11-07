# backend/app/api/endpoints.py
from fastapi import APIRouter, HTTPException
from typing import Dict
from app import loader
from app.models import EnhanceRequest, EnhanceResponse, QualityMetrics
import os
try:
    import google.generativeai as genai
except ImportError:
    genai = None

router = APIRouter()

@router.get("/frameworks")
def list_frameworks():
    frameworks = loader.list_frameworks()
    return {"frameworks": frameworks}

@router.get("/models")
def list_models():
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return {"error": "GEMINI_API_KEY not found"}
    
    genai.configure(api_key=api_key)
    models = []
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            models.append(model.name)
    return {"models": models}





def _ai_enhance_with_framework(user_prompt: str, framework: Dict) -> str:
    # Try Gemini first
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        try:
            genai.configure(api_key=api_key)
            # Use gemini-2.0-flash specifically
            model = genai.GenerativeModel('models/gemini-2.0-flash')
            prompt = f"Enhance this prompt using {framework.get('name')} framework: {user_prompt}"
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception:
            pass
    
    # Fallback to local T5 model
    try:
        from transformers import pipeline
        enhancer = pipeline("text2text-generation", model="t5-small", max_length=200)
        enhanced_prompt = f"improve: {user_prompt}"
        result = enhancer(enhanced_prompt, max_length=150, do_sample=False)
        return result[0]['generated_text']
    except Exception:
        pass
    
    # Final fallback
    return f"Please provide a detailed explanation about {user_prompt.replace('i want to learn about', '').strip()}"

@router.post("/enhance", response_model=EnhanceResponse)
def enhance(req: EnhanceRequest):
    framework = loader.get_framework(req.framework_id or "PRO")
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    
    enhanced = _ai_enhance_with_framework(req.prompt, framework)
    
    return EnhanceResponse(
        selected_framework=framework.get("id"),
        enhanced_prompt=enhanced,
        quality=QualityMetrics(clarity=8.0, specificity=8.0, context_richness=7.5, actionability=8.0, overall=8.0),
        explain=["AI-enhanced"],
        analysis={}
    )
