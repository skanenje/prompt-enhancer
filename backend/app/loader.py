# backend/app/loader.py
import os
import json
from typing import Dict, List

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRAME_DIR = os.path.join(BASE_DIR, "frameworks")

def list_frameworks() -> List[Dict]:
    items = []
    for f in os.listdir(FRAME_DIR):
        if f.endswith(".json"):
            path = os.path.join(FRAME_DIR, f)
            with open(path, "r", encoding="utf-8") as fh:
                try:
                    data = json.load(fh)
                    items.append({"id": data.get("id", f.replace(".json","")), "name": data.get("name"), "description": data.get("description")})
                except Exception:
                    continue
    return items

def get_framework(framework_id: str) -> Dict:
    path = os.path.join(FRAME_DIR, f"{framework_id}.json")
    if not os.path.exists(path):
        # try case insensitive
        for fname in os.listdir(FRAME_DIR):
            if fname.lower() == f"{framework_id.lower()}.json":
                path = os.path.join(FRAME_DIR, fname)
                break
        else:
            return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)

def save_framework_bytes(filename: str, content: bytes):
    # simple save; in prod validate schema
    if not filename.endswith(".json"):
        filename = filename.rsplit(".",1)[0] + ".json"
    path = os.path.join(FRAME_DIR, filename)
    with open(path, "wb") as fh:
        fh.write(content)
    return path
