# backend/app/core/nlp_utils.py
import os
from typing import Optional

try:
    import spacy
    from transformers import pipeline
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False

class NLPManager:
    """Singleton manager for NLP models to avoid reloading"""
    _instance = None
    _spacy_model = None
    _t5_pipeline = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_spacy_model(self):
        if not MODELS_AVAILABLE:
            return None
            
        if self._spacy_model is None:
            try:
                self._spacy_model = spacy.load("en_core_web_sm")
            except OSError:
                # Model not installed
                return None
        return self._spacy_model
    
    def get_t5_pipeline(self):
        if not MODELS_AVAILABLE:
            return None
            
        if self._t5_pipeline is None:
            try:
                self._t5_pipeline = pipeline(
                    "text2text-generation", 
                    model="t5-small",
                    max_length=512,
                    device=-1  # CPU only for compatibility
                )
            except Exception:
                return None
        return self._t5_pipeline

# Global instance
nlp_manager = NLPManager()