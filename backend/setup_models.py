#!/usr/bin/env python3
"""
Setup script to download required NLP models
Run this after installing requirements.txt
"""

import subprocess
import sys

def install_spacy_model():
    """Download spaCy English model"""
    try:
        subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
        print("✓ spaCy English model installed")
    except subprocess.CalledProcessError:
        print("✗ Failed to install spaCy model")
        print("Run manually: python -m spacy download en_core_web_sm")

def test_transformers():
    """Test if transformers can load T5"""
    try:
        from transformers import pipeline
        pipe = pipeline("text2text-generation", model="t5-small")
        print("✓ Transformers T5 model accessible")
        return True
    except Exception as e:
        print(f"✗ Transformers test failed: {e}")
        return False

if __name__ == "__main__":
    print("Setting up NLP models for Prompt Enhancer...")
    install_spacy_model()
    test_transformers()
    print("Setup complete!")