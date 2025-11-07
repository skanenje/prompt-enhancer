# backend/app/api/endpoints.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
from app import loader
from app.core.analyzer import Analyzer
from app.core.selector import Selector
from app.core.synthesizer import Synthesizer
from app.core.evaluator import Evaluator

router = APIRouter()

class EnhanceRequest(BaseModel):
    prompt: str
    framework_id: Optional[str] = None
    fields: Optional[Dict[str, str]] = None
    explain: Optional[bool] = False

class EnhanceResponse(BaseModel):
    selected_framework: str
    enhanced_prompt: str
    quality: float
    explain: Optional[List[str]] = []

@router.get("/frameworks")
def list_frameworks():
    frameworks = loader.list_frameworks()
    return {"frameworks": frameworks}

@router.post("/frameworks/upload")
async def upload_framework(file: UploadFile = File(...)):
    if not file.filename.endswith((".json", ".yaml", ".yml")):
        raise HTTPException(status_code=400, detail="Only JSON/YAML allowed")
    content = await file.read()
    try:
        loader.save_framework_bytes(file.filename, content)
        return {"status": "ok", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auto")
def auto_suggest(payload: Dict[str, str]):
    prompt = payload.get("prompt", "")
    analyzer = Analyzer()
    parsed = analyzer.analyze(prompt)
    selector = Selector()
    suggestions = selector.suggest(parsed, top_n=3)
    return {"suggestions": suggestions, "parsed": parsed}

@router.post("/enhance", response_model=EnhanceResponse)
def enhance(req: EnhanceRequest):
    analyzer = Analyzer()
    parsed = analyzer.analyze(req.prompt)

    # select framework
    if req.framework_id:
        framework = loader.get_framework(req.framework_id)
        if framework is None:
            raise HTTPException(status_code=404, detail="Framework not found")
    else:
        selector = Selector()
        picks = selector.suggest(parsed, top_n=1)
        framework = loader.get_framework(picks[0]["id"])

    synthesizer = Synthesizer()
    enhanced, diag = synthesizer.synthesize(req.prompt, framework, overrides=req.fields or {}, explain=req.explain)

    evaluator = Evaluator()
    score, notes = evaluator.score(enhanced, framework, parsed)

    explain_out = diag + notes
    return EnhanceResponse(
        selected_framework=framework.get("id"),
        enhanced_prompt=enhanced,
        quality=round(score, 2),
        explain=explain_out
    )
