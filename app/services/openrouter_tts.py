import httpx
from typing import Optional, Tuple
from app.config import get_api_key, load_config

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

async def generate_openrouter_speech(
    text: str,
    voice: str = "af_heart",
    model: Optional[str] = None,
    api_key_override: Optional[str] = None,
    timeout: float = 60.0
) -> Tuple[bytes, str]:
    """
    Calls OpenRouter /audio/speech endpoint with Kokoro 82M or other speech models.
    Returns raw audio bytes and MIME type.
    """
    api_key = get_api_key("openrouter", api_key_override)
    if not api_key:
        raise ValueError("OpenRouter API key is not configured. Please add your API key in Settings.")

    if not model:
        cfg = load_config()
        configured_model = cfg.get("default_model", "")
        model = configured_model if configured_model and "kokoro" in configured_model else "hexgrad/kokoro-82m"

    # Normalize voice id
    voice_slug = voice or "af_heart"
    if voice_slug.startswith("kokoro-"):
        voice_slug = voice_slug.replace("kokoro-", "")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://localhost:8000",
        "X-Title": "SPRACH TTS",
        "Content-Type": "application/json"
    }

    url = f"{OPENROUTER_BASE_URL}/audio/speech"
    payload = {
        "model": model,
        "input": text,
        "voice": voice_slug,
        "response_format": "mp3"
    }

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, headers=headers, json=payload)
        if resp.status_code != 200:
            err_msg = resp.text
            try:
                err_data = resp.json()
                if "error" in err_data:
                    err_msg = err_data["error"].get("message", resp.text)
            except Exception:
                pass
            raise RuntimeError(f"OpenRouter API Error ({resp.status_code}): {err_msg}")

        return resp.content, "audio/mp3"
