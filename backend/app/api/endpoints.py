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





def _load_system_prompt() -> str:
    try:
        import json
        with open('/home/zedolph/prompt-enhancer/backend/system_prompt.json', 'r') as f:
            return json.load(f)['system_prompt']
    except:
        return "You are an expert prompt enhancer focused on engineering fundamentals and first principles thinking."

def _ai_enhance_with_framework(user_prompt: str, framework: Dict) -> str:
    # Try Gemini first
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('models/gemini-2.0-flash')
            
            system_prompt = _load_system_prompt()
            
            prompt = f"""
You are a prompt enhancement specialist. Your ONLY job is to improve prompts, NOT to answer them.

Framework: {framework.get('name')} - {framework.get('description')}
Original prompt to enhance: "{user_prompt}"

IMPORTANT: Do NOT answer the question in the original prompt. Instead, rewrite it as a better, more detailed prompt that someone else could use with another ai tool like chatGPT to get maximum information from it.

Enhance this prompt by:
- Making it more specific and detailed
- Adding relevant context and constraints
- Structuring it clearly
- Including expected output format
- Using the selected framework's approach

Return ONLY the enhanced prompt, nothing else:
"""
            
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
    
    # Final fallback with engineering focus
    topic = user_prompt.replace('i want to learn about', '').replace('i want to', '').strip()
    return f"""# Engineering Deep Dive: {topic.title()}

## First Principles Approach
Explain **{topic}** by breaking it down to fundamental components:

### Core Fundamentals
- What are the basic building blocks?
- What physical/mathematical principles govern this?
- How do the fundamental forces/mechanisms work?

### System Architecture
- How do components interact systematically?
- What are the key relationships and dependencies?
- What are the design constraints and trade-offs?

### Engineering Applications
- Real-world implementations and use cases
- Performance metrics and optimization strategies
- Common failure modes and reliability considerations

## Learning Methodology
- Start with basic principles and build complexity gradually
- Include mathematical relationships where relevant
- Provide engineering examples and case studies
- Focus on understanding 'why' things work, not just 'how'

*Approach this from an engineering perspective with systematic, first-principles thinking.*"""

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
