# backend/app/models.py
from pydantic import BaseModel
from typing import Optional, Dict, List

class EnhanceRequest(BaseModel):
    prompt: str
    framework_id: Optional[str] = None
    fields: Optional[Dict[str,str]] = None
    explain: Optional[bool] = False

class QualityMetrics(BaseModel):
    clarity: float
    specificity: float
    context_richness: float
    actionability: float
    overall: float

class EnhanceResponse(BaseModel):
    selected_framework: str
    enhanced_prompt: str
    quality: QualityMetrics
    explain: Optional[List[str]] = []
    analysis: Optional[Dict] = None
