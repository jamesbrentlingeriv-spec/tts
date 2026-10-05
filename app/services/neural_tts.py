import asyncio
import edge_tts
from typing import Optional, Tuple
from pathlib import Path
from app.config import AUDIO_OUTPUT_DIR

DEFAULT_VOICE = "en-US-ChristopherNeural"

async def generate_neural_speech(
    text: str,
    voice: Optional[str] = None,
    rate: str = "+0%",
    pitch: str = "+0Hz"
) -> Tuple[bytes, str]:
    """
    Generates high-fidelity speech using Microsoft Neural TTS.
    Returns native MP3 audio bytes and MIME type.
    Latency is typically 0.4s to 0.9s with zero API fees or rate limits.
    """
    target_voice = voice or DEFAULT_VOICE
    # Clean text
    clean_text = text.strip()
    if not clean_text:
        raise ValueError("Text cannot be empty")

    communicate = edge_tts.Communicate(clean_text, target_voice, rate=rate, pitch=pitch)
    chunks = []
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            chunks.append(chunk["data"])

    if not chunks:
        raise RuntimeError("No audio data received from Neural TTS service")

    audio_bytes = b"".join(chunks)
    return audio_bytes, "audio/mp3"

async def get_or_create_preview(voice_id: str, sample_text: Optional[str] = None) -> str:
    """
    Returns the URL to the cached voice preview, generating it on-demand if not already cached.
    """
    cache_file = AUDIO_OUTPUT_DIR / f"preview_{voice_id}.mp3"
    if cache_file.exists() and cache_file.stat().st_size > 1000:
        return f"/audio/{cache_file.name}"

    text = sample_text or "Hello! I am ready to narrate your stories, articles, and audiobooks in SPRACH."
    raw_mp3, _ = await generate_neural_speech(text, voice=voice_id)
    with open(cache_file, "wb") as f:
        f.write(raw_mp3)

    return f"/audio/{cache_file.name}"
