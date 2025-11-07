# backend/app/core/analyzer.py
import re
from typing import Dict, Any, List
from collections import Counter

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

class Analyzer:
    """
    Advanced NLP analyzer using spaCy for linguistic analysis.
    Provides semantic understanding and context extraction.
    """
    def __init__(self):
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                pass
        
        self.teach_verbs = {"explain","teach","summarize","describe","define"}
        self.plan_nouns = {"plan","goal","milestone","roadmap","strategy"}
        self.analyze_verbs = {"analyze","compare","evaluate","diagnose","inspect"}
        self.technical_keywords = {"iot","mqtt","rest","api","docker","kubernetes","rust","go","python"}

    def analyze(self, text: str) -> Dict[str, Any]:
        result = self._basic_analysis(text)
        
        if self.nlp:
            result.update(self._advanced_analysis(text))
        
        return result
    
    def _basic_analysis(self, text: str) -> Dict[str, Any]:
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
            "audience": audience,
            "word_count": len(text.split()),
            "char_count": len(text)
        }
    
    def _advanced_analysis(self, text: str) -> Dict[str, Any]:
        doc = self.nlp(text)
        
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        sentences = [sent.text for sent in doc.sents]
        subjects = [token.text for token in doc if token.dep_ == "nsubj"]
        objects = [token.text for token in doc if token.dep_ in ["dobj", "pobj"]]
        imperatives = [sent for sent in doc.sents if sent.root.tag_ == "VB"]
        
        avg_sent_length = sum(len(sent.text.split()) for sent in doc.sents) / len(list(doc.sents)) if doc.sents else 0
        
        return {
            "entities": entities,
            "sentences": sentences,
            "subjects": subjects,
            "objects": objects,
            "imperatives": len(imperatives),
            "avg_sentence_length": round(avg_sent_length, 2),
            "complexity_score": self._calculate_complexity(doc)
        }
    
    def _calculate_complexity(self, doc) -> float:
        base_score = len(doc) / 10
        entity_score = len(doc.ents) * 0.5
        dep_score = len([token for token in doc if token.dep_ not in ["punct", "space"]]) * 0.1
        return min(10.0, base_score + entity_score + dep_score)
