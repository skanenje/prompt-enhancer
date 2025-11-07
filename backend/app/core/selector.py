# backend/app/core/selector.py
from typing import Dict, List
from app import loader

class Selector:
    """
    Simple rule-based selector. Replace with embeddings later.
    """
    def __init__(self):
        # load frameworks id list
        self.frameworks = {f["id"]: f for f in loader.list_frameworks()}

    def score_for_framework(self, parsed: Dict, framework_id: str) -> float:
        fid = framework_id.lower()
        score = 0.0
        text = parsed.get("raw", "").lower()
        verbs = parsed.get("verbs", [])
        nouns = parsed.get("nouns", [])
        domains = parsed.get("domains", [])
        tone = parsed.get("tone", "neutral")
        
        # DRIP - Precision and control
        if fid == "drip":
            if any(word in text for word in ["precise", "specific", "control", "exact", "detailed"]):
                score += 2.0
        
        # PEEL - Human, relatable writing
        if fid == "peel":
            if any(word in text for word in ["relatable", "human", "personal", "emotional", "connect"]):
                score += 2.0
        
        # PRO - Problem solving
        if fid == "pro":
            if any(word in text for word in ["stuck", "problem", "help", "struggling", "issue", "challenge"]):
                score += 2.5
        
        # TAG - Marketing/optimization
        if fid == "tag":
            if any(word in text for word in ["marketing", "optimize", "conversion", "campaign"]):
                score += 2.0
        
        # ROSES - Structured responses
        if fid == "roses":
            if any(word in text for word in ["structured", "step by step", "format", "organize"]):
                score += 1.8
        
        # IDEA - Content creation
        if fid == "idea":
            if any(word in text for word in ["create", "content", "write", "post", "article", "blog"]):
                score += 2.0
        
        # CLEAR - Emotional content
        if fid == "clear":
            if parsed.get("audience") == "marketing":
                score += 1.5
            if any(word in text for word in ["emotional", "inspiring", "motivating", "engaging"]):
                score += 1.8
            if tone in ["casual","urgent"]:
                score += 0.5
        
        # APE - Teaching/explanation
        if fid == "ape":
            if any(v in verbs for v in ["explain","teach","summarize"]):
                score += 1.2
        
        # STAGE - Project planning
        if fid == "stage":
            if any(n in nouns for n in ["plan","goal","strategy","roadmap"]):
                score += 1.4
        
        # Tech bias for APE and STAGE
        if fid in ["ape","stage"] and domains:
            score += 0.3
        
        return score

    def suggest(self, parsed: Dict, top_n: int = 3) -> List[Dict]:
        available = loader.list_frameworks()
        scored = []
        for f in available:
            sc = self.score_for_framework(parsed, f["id"])
            scored.append({"id": f["id"], "name": f["name"], "score": round(sc, 3)})
        scored.sort(key=lambda x: x["score"], reverse=True)
        # always return something even if score zero
        return scored[:top_n]
