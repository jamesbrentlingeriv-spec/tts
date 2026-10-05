from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path
from app.services.storage import load_voices, save_custom_voice, delete_custom_voice, get_voice_by_id, GEMINI_VOICES
from app.services.neural_tts import generate_neural_speech, get_or_create_preview
from app.services.openrouter_tts import generate_openrouter_speech
from app.services.gemini_tts import generate_gemini_speech
from app.config import AUDIO_OUTPUT_DIR

router = APIRouter(prefix="/api/voices", tags=["voices"])

class VoiceCreate(BaseModel):
    name: str
    gender: Optional[str] = "Male"
    base_voice: str = "en-US-ChristopherNeural"
    language: Optional[str] = "en-US"
    accent: Optional[str] = "American"
    description: Optional[str] = ""
    tags: Optional[List[str]] = []

class VoicePreviewRequest(BaseModel):
    voice_id: Optional[str] = "en-US-ChristopherNeural"
    sample_text: Optional[str] = "Hello! I am ready to narrate your stories, articles, and audiobooks in SPRACH."

@router.get("")
def list_voices(engine: Optional[str] = Query("all")):
    """
    Returns voice catalog filtered by engine ('microsoft_neural', 'kokoro', or 'all').
    Defaults to 'all' so the frontend has access to all voices for instant switching.
    """
    return load_voices(engine=engine or "all")

@router.get("/{voice_id}")
def get_voice(voice_id: str):
    v = get_voice_by_id(voice_id)
    if not v:
        raise HTTPException(status_code=404, detail="Voice not found")
    return v

@router.post("")
def create_voice(voice_in: VoiceCreate):
    data = voice_in.model_dump()
    saved = save_custom_voice(data)
    return saved

@router.put("/{voice_id}")
def update_voice(voice_id: str, voice_in: VoiceCreate):
    existing = get_voice_by_id(voice_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Voice not found")
    if not existing.get("is_custom"):
        raise HTTPException(status_code=400, detail="Cannot modify built-in voices")
    
    data = voice_in.model_dump()
    data["id"] = voice_id
    saved = save_custom_voice(data)
    return saved

@router.delete("/{voice_id}")
def remove_voice(voice_id: str):
    existing = get_voice_by_id(voice_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Voice not found")
    if not existing.get("is_custom"):
        raise HTTPException(status_code=400, detail="Cannot delete built-in voices")
    
    deleted = delete_custom_voice(voice_id)
    return {"status": "deleted" if deleted else "failed"}

@router.post("/preview")
async def preview_voice(req: VoicePreviewRequest):
    """
    Returns an instant 1-sentence audio preview.
    If cached on disk (preview_{voice_id}.mp3), it serves immediately in <0.01s.
    If not cached:
      - Microsoft Neural voices are generated via Edge TTS (~0.8s) and cached.
      - Kokoro voices are generated via OpenRouter Kokoro-82M and cached to disk forever.
    """
    target_voice = (req.voice_id or "en-US-ChristopherNeural").strip()
    sample_text = (req.sample_text or "Hello! I am ready to narrate your stories, articles, and audiobooks in SPRACH.").strip()
    
    cache_file = AUDIO_OUTPUT_DIR / f"preview_{target_voice}.mp3"

    # 1. Instant Cache Hit: Return immediately!
    if cache_file.exists() and cache_file.stat().st_size > 500:
        preview_url = f"/audio/{cache_file.name}"
        return {
            "status": "success",
            "cached": True,
            "audio_url": preview_url,
            "mp3_url": preview_url,
            "m4a_url": preview_url,
            "wav_url": preview_url
        }

    # 2. Cache Miss: Generate and cache to disk
    try:
        g_ids = {v["id"].lower() for v in GEMINI_VOICES}
        is_gemini = target_voice.lower() in g_ids or target_voice.lower().startswith("gemini-") or target_voice.lower() in ["puck", "charon", "kore", "fenrir", "aoede"]
        is_neural = "Neural" in target_voice or (target_voice.startswith("en-") and not target_voice.startswith("ef_"))

        if is_gemini:
            raw_audio, _ = await generate_gemini_speech(sample_text, voice=target_voice)
        elif is_neural:
            raw_audio, _ = await generate_neural_speech(sample_text, voice=target_voice)
        else:
            raw_audio, _ = await generate_openrouter_speech(sample_text, voice=target_voice)

        with open(cache_file, "wb") as f:
            f.write(raw_audio)

        preview_url = f"/audio/{cache_file.name}"
        return {
            "status": "success",
            "cached": False,
            "audio_url": preview_url,
            "mp3_url": preview_url,
            "m4a_url": preview_url,
            "wav_url": preview_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def _cache_single_voice(voice_id: str):
    cache_file = AUDIO_OUTPUT_DIR / f"preview_{voice_id}.mp3"
    if cache_file.exists() and cache_file.stat().st_size > 500:
        return
    try:
        sample = "Hello! I am ready to narrate your stories, articles, and audiobooks in SPRACH."
        audio, _ = await generate_openrouter_speech(sample, voice=voice_id, timeout=45.0)
        with open(cache_file, "wb") as f:
            f.write(audio)
    except Exception as e:
        pass

async def _cache_all_kokoro_task():
    from app.services.storage import KOKORO_VOICES
    for v in KOKORO_VOICES:
        await _cache_single_voice(v["id"])

@router.post("/cache-all")
async def trigger_cache_all(background_tasks: BackgroundTasks):
    background_tasks.add_task(_cache_all_kokoro_task)
    return {"status": "started", "message": "Pre-caching Kokoro previews in background"}

