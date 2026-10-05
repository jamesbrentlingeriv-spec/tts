import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
AUDIO_OUTPUT_DIR = DATA_DIR / "audio_output"
CONFIG_FILE = DATA_DIR / "config.json"
VOICES_FILE = DATA_DIR / "voices.json"
HISTORY_FILE = DATA_DIR / "history.json"

for d in [DATA_DIR, AUDIO_OUTPUT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

DEFAULT_CONFIG = {
    "engine": "gemini",
    "gemini_api_key": os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", ""),
    "openrouter_api_key": os.getenv("OPENROUTER_API_KEY", ""),
    "default_model": "gemini-2.0-flash",
    "default_voice": "Puck",
    "default_format": "mp3",
    "chunk_size": 1000
}

def normalize_key(k: str) -> str:
    if not k:
        return ""
    k = k.strip().strip('"').strip("'")
    if k.lower().startswith("sk-or-v1-"):
        return "sk-or-v1-" + k[9:]
    elif k.lower().startswith("sk-"):
        return "sk-" + k[3:]
    return k

def load_config() -> Dict[str, Any]:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                cfg = DEFAULT_CONFIG.copy()
                cfg.update(saved)
                # Remove obsolete elevenlabs key if present
                cfg.pop("elevenlabs_api_key", None)
                if "gemini_api_key" in cfg:
                    cfg["gemini_api_key"] = cfg["gemini_api_key"].strip().strip('"').strip("'")
                if "openrouter_api_key" in cfg:
                    cfg["openrouter_api_key"] = normalize_key(cfg["openrouter_api_key"])
                return cfg
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(updates: Dict[str, Any]) -> Dict[str, Any]:
    cfg = load_config()
    cfg.update(updates)
    cfg.pop("elevenlabs_api_key", None)
    if "gemini_api_key" in cfg:
        cfg["gemini_api_key"] = cfg["gemini_api_key"].strip().strip('"').strip("'")
    if "openrouter_api_key" in cfg:
        cfg["openrouter_api_key"] = normalize_key(cfg["openrouter_api_key"])
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    return cfg

def get_api_key(provider_or_override: Optional[str] = None, override_key: Optional[str] = None) -> str:
    if override_key and override_key.strip():
        return normalize_key(override_key)
    
    cfg = load_config()
    prov = (provider_or_override or "").lower().strip()
    
    if prov in ["gemini", "google"]:
        return cfg.get("gemini_api_key", "").strip() or os.getenv("GEMINI_API_KEY", "").strip() or os.getenv("GOOGLE_API_KEY", "").strip()
    elif prov in ["openrouter", "kokoro"]:
        return cfg.get("openrouter_api_key", "").strip() or os.getenv("OPENROUTER_API_KEY", "").strip()
    
    # If a specific key string was passed as provider_or_override that isn't a known provider name
    if provider_or_override and provider_or_override not in ["openrouter", "gemini", "google", "kokoro"]:
        return normalize_key(provider_or_override)
    
    # Fallback checking active engine
    if cfg.get("engine") == "gemini":
        return cfg.get("gemini_api_key", "").strip() or os.getenv("GEMINI_API_KEY", "").strip() or os.getenv("GOOGLE_API_KEY", "").strip()
    return normalize_key(cfg.get("openrouter_api_key", "").strip() or os.getenv("OPENROUTER_API_KEY", "").strip())
