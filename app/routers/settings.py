import time
import httpx
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.config import load_config, save_config, normalize_key
import edge_tts

router = APIRouter(prefix="/api/settings", tags=["settings"])

class SettingsUpdate(BaseModel):
    engine: Optional[str] = None
    gemini_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    default_model: Optional[str] = None
    default_voice: Optional[str] = None
    default_format: Optional[str] = None
    chunk_size: Optional[int] = None

@router.get("")
def get_settings():
    cfg = load_config()
    engine = cfg.get("engine", "gemini")
    raw_key = cfg.get("openrouter_api_key", "")
    masked_key = f"{raw_key[:10]}...{raw_key[-4:]}" if len(raw_key) > 16 else ("***" if raw_key else "")
    raw_gem_key = cfg.get("gemini_api_key", "")
    masked_gem_key = f"{raw_gem_key[:6]}...{raw_gem_key[-4:]}" if len(raw_gem_key) > 10 else ("***" if raw_gem_key else "")

    engine_names = {
        "gemini": "Google Gemini 2.0 Flash Audio",
        "kokoro": "Kokoro 82M (OpenRouter)",
        "microsoft_neural": "Microsoft Neural TTS"
    }

    return {
        "engine": engine,
        "engine_name": engine_names.get(engine, "Google Gemini 2.0 Flash Audio"),
        "is_free": engine == "microsoft_neural",
        "requires_api_key": engine in ("gemini", "kokoro"),
        "has_gemini_key": bool(raw_gem_key),
        "masked_gemini_key": masked_gem_key,
        "has_openrouter_key": bool(raw_key),
        "masked_openrouter_key": masked_key,
        "default_model": cfg.get("default_model", "gemini-2.0-flash" if engine == "gemini" else ("Microsoft Neural (Edge)" if engine == "microsoft_neural" else "hexgrad/kokoro-82m")),
        "default_voice": cfg.get("default_voice", "Puck" if engine == "gemini" else ("en-US-ChristopherNeural" if engine == "microsoft_neural" else "af_heart")),
        "default_format": cfg.get("default_format", "mp3"),
        "chunk_size": cfg.get("chunk_size", 1000)
    }

@router.post("")
def update_settings(updates: SettingsUpdate):
    data = updates.model_dump(exclude_unset=True)
    cfg = load_config()
    clean_data = {}

    for k, v in data.items():
        if v is not None:
            clean_data[k] = v

    # Handle Gemini API key
    if "gemini_api_key" in clean_data:
        key_val = clean_data["gemini_api_key"].strip().strip('"').strip("'")
        clean_data["gemini_api_key"] = key_val

    # Handle OpenRouter API key normalization
    if "openrouter_api_key" in clean_data:
        key_val = clean_data["openrouter_api_key"].strip()
        clean_data["openrouter_api_key"] = normalize_key(key_val) if key_val else ""

    # Engine selection and voice alignment
    if "engine" in clean_data:
        eng = clean_data["engine"]
        if eng == "gemini":
            clean_data["default_model"] = "gemini-2.0-flash"
            current_voice = clean_data.get("default_voice") or cfg.get("default_voice", "")
            if not current_voice or current_voice not in ["Puck", "Charon", "Kore", "Fenrir", "Aoede"]:
                clean_data["default_voice"] = "Puck"
        elif eng == "kokoro":
            clean_data["default_model"] = "hexgrad/kokoro-82m"
            current_voice = clean_data.get("default_voice") or cfg.get("default_voice", "")
            if not current_voice or "Neural" in current_voice or current_voice in ["Puck", "Charon", "Kore", "Fenrir", "Aoede"]:
                clean_data["default_voice"] = "af_heart"
        elif eng == "microsoft_neural":
            clean_data["default_model"] = "Microsoft Neural (Edge)"
            current_voice = clean_data.get("default_voice") or cfg.get("default_voice", "")
            if not current_voice or not "Neural" in current_voice:
                clean_data["default_voice"] = "en-US-ChristopherNeural"

    updated = save_config(clean_data)
    engine = updated.get("engine", "gemini")

    engine_names = {
        "gemini": "Google Gemini 2.0 Flash Audio",
        "kokoro": "Kokoro 82M (OpenRouter)",
        "microsoft_neural": "Microsoft Neural TTS"
    }

    return {
        "status": "success",
        "engine": engine,
        "engine_name": engine_names.get(engine, "Google Gemini 2.0 Flash Audio"),
        "default_model": updated.get("default_model"),
        "default_voice": updated.get("default_voice"),
        "default_format": updated.get("default_format"),
        "chunk_size": updated.get("chunk_size")
    }

@router.get("/verify")
async def verify_engine():
    cfg = load_config()
    engine = cfg.get("engine", "gemini")
    t0 = time.time()
    valid = False
    error = None
    ms = 0

    if engine == "gemini":
        key = cfg.get("gemini_api_key", "").strip()
        if not key:
            return {
                "engine": "gemini",
                "valid": False,
                "latency_ms": 0,
                "error": "No Gemini API key provided. Please enter your Google Gemini API key.",
                "is_free": False,
                "provider": "Google Gemini API"
            }
        from app.services.gemini_tts import verify_gemini_key
        res = await verify_gemini_key(key)
        return {
            "engine": "gemini",
            "valid": res["valid"],
            "latency_ms": res.get("latency_ms", 0),
            "error": res.get("error"),
            "is_free": False,
            "provider": "Google Gemini (2.0 Flash Audio)",
            "model_count": res.get("model_count")
        }

    if engine == "kokoro":
        key = cfg.get("openrouter_api_key", "").strip()
        if not key:
            return {
                "engine": "kokoro",
                "valid": False,
                "latency_ms": 0,
                "error": "No OpenRouter API key provided. Please enter your key.",
                "is_free": False,
                "provider": "OpenRouter (Kokoro-82M)"
            }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(
                    "https://openrouter.ai/api/v1/auth/key",
                    headers={"Authorization": f"Bearer {key}"}
                )
                ms = round((time.time() - t0) * 1000)
                if res.status_code == 200:
                    valid = True
                else:
                    error = f"OpenRouter returned {res.status_code}: {res.text}"
        except Exception as e:
            error = str(e)

        return {
            "engine": "kokoro",
            "valid": valid,
            "latency_ms": ms,
            "error": error,
            "is_free": False,
            "provider": "OpenRouter API"
        }

    # Default: Microsoft Neural
    try:
        c = edge_tts.Communicate("SPRACH connected.", "en-US-ChristopherNeural")
        async for chunk in c.stream():
            if chunk["type"] == "audio":
                valid = True
                break
        ms = round((time.time() - t0) * 1000)
    except Exception as e:
        error = str(e)

    return {
        "engine": "microsoft_neural",
        "valid": valid,
        "latency_ms": ms,
        "error": error,
        "is_free": True,
        "provider": "Microsoft Azure Neural CDN"
    }

class KeyClearRequest(BaseModel):
    key_name: str  # "openrouter", "gemini", or "all"

@router.post("/clear-key")
def clear_api_key(req: KeyClearRequest):
    """Explicitly blocks and clears an API key from configuration."""
    updates = {}
    if req.key_name in ["openrouter", "all"]:
        updates["openrouter_api_key"] = ""
    if req.key_name in ["gemini", "all"]:
        updates["gemini_api_key"] = ""
    updated = save_config(updates)
    return {
        "status": "success",
        "cleared": req.key_name,
        "has_openrouter_key": bool(updated.get("openrouter_api_key")),
        "has_gemini_key": bool(updated.get("gemini_api_key"))
    }


