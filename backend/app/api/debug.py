# backend/app/api/debug.py
from fastapi import APIRouter
from app.core.analyzer import Analyzer
from app.core.synthesizer import Synthesizer
from app import loader

router = APIRouter()

@router.post("/debug/analyze")
def debug_analyze(payload: dict):
    """Debug endpoint to see raw analysis results"""
    prompt = payload.get("prompt", "")
    analyzer = Analyzer()
    result = analyzer.analyze(prompt)
    return {"prompt": prompt, "analysis": result}

@router.post("/debug/infer")
def debug_infer(payload: dict):
    """Debug endpoint to test field inference"""
    prompt = payload.get("prompt", "")
    framework_id = payload.get("framework_id", "ROSES")
    
    framework = loader.get_framework(framework_id)
    if not framework:
        return {"error": "Framework not found"}
    
    synthesizer = Synthesizer()
    inferences = {}
    
    for field_name in framework.get("fields", {}).keys():
        inferred = synthesizer.infer_field(field_name, prompt)
        inferences[field_name] = inferred
    
    return {
        "prompt": prompt,
        "framework": framework_id,
        "template": framework.get("template"),
        "inferences": inferences
    }