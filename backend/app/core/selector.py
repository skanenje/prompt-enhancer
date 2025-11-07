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
        # heuristic rules
        verbs = parsed.get("verbs", [])
        nouns = parsed.get("nouns", [])
        domains = parsed.get("domains", [])
        tone = parsed.get("tone", "neutral")
        if fid in ["clear"]:
            # good for marketing / emotional content
            if parsed.get("audience") == "marketing":
                score += 1.5
            if tone in ["casual","urgent"]:
                score += 0.5
        if fid in ["ape"]:
            if any(v in verbs for v in ["explain","teach","summarize"]):
                score += 1.2
        if fid in ["stage"]:
            if any(n in nouns for n in ["plan","goal","strategy","roadmap"]):
                score += 1.4
        # tech bias
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
