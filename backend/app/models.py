# backend/app/models.py
from pydantic import BaseModel
from typing import Optional, Dict, List

class EnhanceRequest(BaseModel):
    prompt: str
    framework_id: Optional[str] = None
    fields: Optional[Dict[str,str]] = None
    explain: Optional[bool] = False

class EnhanceResponse(BaseModel):
    selected_framework: str
    enhanced_prompt: str
    quality: float
    explain: Optional[List[str]] = []
