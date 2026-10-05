import base64
import json
import time
import httpx
from typing import Tuple, Optional, Dict, Any
from app.config import get_api_key, load_config
from app.services.audio_stitcher import pcm_to_wav_bytes

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

def resolve_gemini_model(cfg_model: Optional[str] = None) -> str:
    if cfg_model and cfg_model.strip():
        m = cfg_model.strip().lower()
        if "gemini" in m:
            return cfg_model.strip()
    return "gemini-2.0-flash"

async def generate_gemini_speech(
    text: str,
    voice: str = "Puck",
    model: Optional[str] = None,
    custom_persona: Optional[str] = None,
    pacing: Optional[str] = None,
    emotion: Optional[str] = None,
    api_key_override: Optional[str] = None,
    timeout: float = 60.0
) -> Tuple[bytes, str]:
    """
    Generates high fidelity speech using Google Gemini 2.0 Audio modality.
    Supports system instructions for voice persona, pacing, and emotional expression.
    """
    api_key = api_key_override or get_api_key("gemini")
    if not api_key:
        raise ValueError("Google Gemini API key is not configured. Please add your API key in Settings.")

    cfg = load_config()
    target_model = resolve_gemini_model(model or cfg.get("default_model"))
    target_voice = voice.strip() if voice else "Puck"
    # Capitalize standard Gemini voice names if lowercase
    voice_map = {
        "puck": "Puck",
        "charon": "Charon",
        "kore": "Kore",
        "fenrir": "Fenrir",
        "aoede": "Aoede"
    }
    target_voice = voice_map.get(target_voice.lower(), target_voice)

    # Build prompt with optional persona/style guidance
    prompt_parts = []
    style_guidance = []
    if custom_persona and custom_persona.strip():
        style_guidance.append(f"Persona instruction: {custom_persona.strip()}")
    if pacing and pacing.strip():
        style_guidance.append(f"Speaking pace: {pacing.strip()}")
    if emotion and emotion.strip():
        style_guidance.append(f"Tone/Emotion: {emotion.strip()}")

    if style_guidance:
        style_prompt = " ".join(style_guidance)
        prompt_parts.append({"text": f"[{style_prompt}]\nRead the following text aloud with natural inflection:\n{text}"})
    else:
        prompt_parts.append({"text": text})

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": prompt_parts
            }
        ],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": target_voice
                    }
                }
            }
        }
    }

    url = f"{GEMINI_API_BASE}/{target_model}:generateContent?key={api_key}"

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        if resp.status_code != 200:
            err_msg = resp.text
            try:
                err_json = resp.json()
                if "error" in err_json and "message" in err_json["error"]:
                    err_msg = err_json["error"]["message"]
            except Exception:
                pass
            raise RuntimeError(f"Gemini API Error ({resp.status_code}): {err_msg}")

        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            feedback = data.get("promptFeedback", {})
            raise RuntimeError(f"No speech candidate returned by Gemini. Feedback: {feedback}")

        parts = candidates[0].get("content", {}).get("parts", [])
        audio_data_base64 = None
        mime_type = "audio/wav"

        for part in parts:
            if "inlineData" in part:
                inline = part["inlineData"]
                audio_data_base64 = inline.get("data")
                mime_type = inline.get("mimeType", "audio/wav")
                break

        if not audio_data_base64:
            # Check if Gemini returned text instead
            text_parts = [p.get("text") for p in parts if "text" in p]
            if text_parts:
                raise RuntimeError(f"Gemini returned text instead of audio: '{text_parts[0][:100]}...'")
            raise RuntimeError("Gemini did not return any audio data in response.")

        raw_pcm_bytes = base64.b64decode(audio_data_base64)
        # Convert raw PCM (Gemini default 24kHz 16-bit mono) to WAV
        wav_bytes = pcm_to_wav_bytes(raw_pcm_bytes, sample_rate=24000, channels=1, sample_width=2)
        return wav_bytes, "audio/wav"

async def verify_gemini_key(api_key: str) -> Dict[str, Any]:
    """Tests Gemini API key validity by querying models list or generating a test token."""
    t0 = time.time()
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            latency = round((time.time() - t0) * 1000)
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                has_flash = any("gemini-2.0-flash" in m or "flash" in m for m in models)
                return {
                    "valid": True,
                    "latency_ms": latency,
                    "has_flash_audio": has_flash,
                    "model_count": len(models)
                }
            else:
                err_text = resp.text
                try:
                    err_json = resp.json()
                    err_text = err_json.get("error", {}).get("message", err_text)
                except Exception:
                    pass
                return {
                    "valid": False,
                    "latency_ms": latency,
                    "error": f"Gemini Error ({resp.status_code}): {err_text}"
                }
    except Exception as e:
        return {
            "valid": False,
            "latency_ms": round((time.time() - t0) * 1000),
            "error": str(e)
        }
