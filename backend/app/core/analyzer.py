# backend/app/core/analyzer.py
import re
from typing import Dict, Any

class Analyzer:
    """
    Lightweight analyzer using regex/heuristics.
    Replace or extend with spaCy/transformers for production.
    """
    def __init__(self):
        # small keyword maps to domain or tone
        self.teach_verbs = {"explain","teach","summarize","describe","define"}
        self.plan_nouns = {"plan","goal","milestone","roadmap","strategy"}
        self.analyze_verbs = {"analyze","compare","evaluate","diagnose","inspect"}
        self.technical_keywords = {"iot","mqtt","rest","api","docker","kubernetes","rust","go","python"}

    def analyze(self, text: str) -> Dict[str, Any]:
        text_l = text.lower()
        tokens = re.findall(r"[a-zA-Z]+", text_l)
        verbs = [t for t in tokens if t in self.teach_verbs.union(self.analyze_verbs)]
        nouns = [t for t in tokens if t in self.plan_nouns]
        domains = [k for k in self.technical_keywords if k in text_l]
        tone = "neutral"
        if any(w in text_l for w in ["urgent","asap","immediately","now"]):
            tone = "urgent"
        if any(w in text_l for w in ["fun","playful","casual","joking"]):
            tone = "casual"
        # audience heuristics
        audience = None
        if "linkedin" in text_l or "post" in text_l or "twitter" in text_l or "subject line" in text_l:
            audience = "marketing"
        if "student" in text_l or "class" in text_l or "lecture" in text_l:
            audience = "student"
        return {
            "raw": text,
            "verbs": list(set(verbs)),
            "nouns": list(set(nouns)),
            "domains": domains,
            "tone": tone,
            "audience": audience
        }
