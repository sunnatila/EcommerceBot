import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
TEXTS_PATH = BASE_DIR / "data" / "texts.json"

_texts_cache = None

def load_texts():
    global _texts_cache
    if _texts_cache is None:
        with TEXTS_PATH.open("r", encoding="utf-8") as f:
            _texts_cache = json.load(f)
    return _texts_cache

def get_text(key: str, default: str = "") -> str:
    texts = load_texts()
    return texts.get(key, default)

def set_text(key: str, value: str) -> None:
    texts = load_texts()
    texts[key] = value
    with TEXTS_PATH.open("w", encoding="utf-8") as f:
        json.dump(texts, f, ensure_ascii=False, indent=2)
    # invalidate cache so subsequent reads get updated content
    global _texts_cache
    _texts_cache = None
