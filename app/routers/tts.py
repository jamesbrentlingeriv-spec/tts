import uuid
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from app.services.neural_tts import generate_neural_speech
from app.services.openrouter_tts import generate_openrouter_speech
from app.services.gemini_tts import generate_gemini_speech
from app.services.audio_stitcher import save_and_transcode, stitch_chunks
from app.services.chunker import chunk_text, detect_chapters, extract_text_from_file
from app.services.storage import add_history_entry, get_voice_by_id, GEMINI_VOICES
from app.config import AUDIO_OUTPUT_DIR

router = APIRouter(prefix="/api/tts", tags=["tts"])

def is_gemini_voice(voice_id: str, voice_info: Optional[Dict[str, Any]] = None) -> bool:
    if voice_info:
        if voice_info.get("provider") == "gemini" or voice_info.get("category") == "gemini":
            return True
    g_ids = {v["id"].lower() for v in GEMINI_VOICES}
    vid = voice_id.lower().strip()
    return vid in g_ids or vid.startswith("gemini-") or vid in ["puck", "charon", "kore", "fenrir", "aoede"]

def is_kokoro_voice(voice_id: str, voice_info: Optional[Dict[str, Any]] = None) -> bool:
    vid = voice_id.lower().strip()
    if voice_info:
        if voice_info.get("provider") == "openrouter" or voice_info.get("category") == "kokoro":
            return True
        if voice_info.get("provider") in ("microsoft", "gemini"):
            return False
    return (
        vid.startswith(("af_", "am_", "bf_", "bm_", "zf_", "zm_", "jf_", "jm_", "ef_", "em_", "ff_", "hf_", "hm_"))
        or "kokoro" in vid
    )

class QuickTTSRequest(BaseModel):
    text: str
    voice_id: Optional[str] = "Puck"
    custom_persona: Optional[str] = None
    pacing: Optional[str] = None
    emotion: Optional[str] = None
    preferred_format: Optional[str] = "mp3"
    api_key_override: Optional[str] = None

class DocumentParseRequest(BaseModel):
    text: Optional[str] = None
    chunk_size: Optional[int] = 1000

class ChunkGenerateRequest(BaseModel):
    chunk_id: str
    text: str
    voice_id: str = "Puck"
    custom_persona: Optional[str] = None
    pacing: Optional[str] = None
    emotion: Optional[str] = None
    api_key_override: Optional[str] = None

class StitchRequest(BaseModel):
    book_title: str
    chunk_files: List[str]  # e.g. ["tts_abc.wav", "tts_def.wav"] or audio URLs
    voice_name: Optional[str] = "Christopher (Flagship)"

@router.post("/quick")
async def generate_quick_tts(req: QuickTTSRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    voice_id = req.voice_id or "en-US-ChristopherNeural"
    voice_info = get_voice_by_id(voice_id)
    voice_label = voice_info["name"] if voice_info else voice_id

    try:
        if is_gemini_voice(voice_id, voice_info):
            raw_audio_bytes, mime = await generate_gemini_speech(
                text=text,
                voice=voice_id,
                custom_persona=req.custom_persona,
                pacing=req.pacing,
                emotion=req.emotion,
                api_key_override=req.api_key_override
            )
            provider_name = "gemini"
            model_name = "Google Gemini 2.0 Flash Audio"
        elif is_kokoro_voice(voice_id, voice_info):
            raw_audio_bytes, mime = await generate_openrouter_speech(
                text=text,
                voice=voice_id,
                api_key_override=req.api_key_override
            )
            provider_name = "openrouter"
            model_name = "Kokoro 82M (OpenRouter)"
        else:
            raw_audio_bytes, mime = await generate_neural_speech(
                text=text,
                voice=voice_id
            )
            provider_name = "microsoft"
            model_name = "Microsoft Neural (Edge)"

        # Save and transcode to MP3, M4A, WAV
        audio_info = save_and_transcode(
            raw_audio_bytes=raw_audio_bytes,
            preferred_format=req.preferred_format or "mp3"
        )

        # Store in history
        history_entry = {
            "title": text[:60] + ("..." if len(text) > 60 else ""),
            "full_text": text,
            "type": "quick",
            "provider": provider_name,
            "model": model_name,
            "voice": voice_label,
            "mp3_url": audio_info["mp3"],
            "m4a_url": audio_info["m4a"],
            "wav_url": audio_info["wav"],
            "char_count": len(text),
            "word_count": len(text.split()),
            "created_at": time.time()
        }
        add_history_entry(history_entry)

        return {
            "status": "success",
            "audio_url": audio_info["preferred"],
            "mp3_url": audio_info["mp3"],
            "m4a_url": audio_info["m4a"],
            "wav_url": audio_info["wav"],
            "metadata": history_entry
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/parse-document")
async def parse_document(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None),
    chunk_size: Optional[int] = Form(1000)
):
    """
    Parses an uploaded file (.txt, .md, .pdf, .epub) or pasted raw text.
    Returns list of smart chunks and chapter breakdown.
    """
    text_content = ""
    source_filename = "document"

    if file and file.filename:
        source_filename = file.filename
        temp_path = AUDIO_OUTPUT_DIR / f"upload_{uuid.uuid4().hex[:8]}_{file.filename}"
        try:
            content = await file.read()
            with open(temp_path, "wb") as f:
                f.write(content)
            text_content = extract_text_from_file(temp_path, file.filename)
        finally:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass
    elif raw_text and raw_text.strip():
        text_content = raw_text.strip()
    else:
        raise HTTPException(status_code=400, detail="Please upload a file or paste text.")

    if not text_content:
        raise HTTPException(status_code=400, detail="No readable text found in document.")

    # Detect chapters
    chapters = detect_chapters(text_content)

    # Chunk entire document or by chapters
    chunks = chunk_text(text_content, max_chars=chunk_size or 1000)
    
    total_words = len(text_content.split())
    # Approx 150 words per minute speaking rate
    est_duration_minutes = round(total_words / 150, 1)

    return {
        "title": Path(source_filename).stem.replace("_", " ").title(),
        "total_chars": len(text_content),
        "total_words": total_words,
        "est_duration_minutes": est_duration_minutes,
        "chunk_count": len(chunks),
        "chunks": chunks,
        "chapter_count": len(chapters),
        "chapters": [{"title": c["title"], "word_count": c["word_count"]} for c in chapters]
    }

@router.post("/audiobook/generate-chunk")
async def generate_audiobook_chunk(req: ChunkGenerateRequest):
    """
    Generates audio for a single chunk of an audiobook using the selected voice.
    Dynamically routes to Microsoft Neural or OpenRouter Kokoro based on voice.
    """
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Chunk text cannot be empty.")

    chunk_base_name = f"chunk_{req.chunk_id}_{uuid.uuid4().hex[:6]}"
    voice_id = req.voice_id or "en-US-ChristopherNeural"
    voice_info = get_voice_by_id(voice_id)

    try:
        if is_gemini_voice(voice_id, voice_info):
            raw_audio_bytes, mime = await generate_gemini_speech(
                text=text,
                voice=voice_id,
                custom_persona=req.custom_persona,
                pacing=req.pacing,
                emotion=req.emotion,
                api_key_override=req.api_key_override
            )
        elif is_kokoro_voice(voice_id, voice_info):
            raw_audio_bytes, mime = await generate_openrouter_speech(
                text=text,
                voice=voice_id,
                api_key_override=req.api_key_override
            )
        else:
            raw_audio_bytes, mime = await generate_neural_speech(
                text=text,
                voice=voice_id
            )

        audio_info = save_and_transcode(
            raw_audio_bytes=raw_audio_bytes,
            base_name=chunk_base_name,
            preferred_format="mp3"
        )

        return {
            "chunk_id": req.chunk_id,
            "status": "completed",
            "audio_url": audio_info["mp3"],
            "mp3_url": audio_info["mp3"],
            "m4a_url": audio_info["m4a"],
            "wav_url": audio_info["wav"],
            "wav_filename": Path(audio_info["wav_path"]).name
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audiobook/stitch")
async def stitch_audiobook(req: StitchRequest):
    """
    Concatenates all completed chunk audio files into a unified master audiobook file.
    Outputs both .mp3 and .m4a!
    """
    if not req.chunk_files:
        raise HTTPException(status_code=400, detail="No audio chunks provided to stitch.")

    # Resolve local file paths
    resolved_paths: List[Path] = []
    for item in req.chunk_files:
        filename = item.split("/")[-1]
        wav_candidate = AUDIO_OUTPUT_DIR / f"{Path(filename).stem}.wav"
        if wav_candidate.exists():
            resolved_paths.append(wav_candidate)
        else:
            cand = AUDIO_OUTPUT_DIR / filename
            if cand.exists():
                resolved_paths.append(cand)

    if not resolved_paths:
        raise HTTPException(status_code=404, detail="None of the specified chunk audio files were found on server.")

    try:
        stitch_result = stitch_chunks(
            chunk_paths=resolved_paths,
            book_title=req.book_title,
            output_formats=["mp3", "m4a"]
        )

        # Add master book to library history
        history_entry = {
            "title": req.book_title,
            "full_text": f"Complete audiobook created from {len(resolved_paths)} chapters/chunks.",
            "type": "audiobook",
            "provider": "microsoft",
            "model": "Microsoft Neural (Edge)",
            "voice": req.voice_name or "Christopher (Flagship)",
            "mp3_url": stitch_result["mp3"],
            "m4a_url": stitch_result["m4a"],
            "wav_url": stitch_result.get("wav", stitch_result["mp3"]),
            "chunk_count": len(resolved_paths),
            "created_at": time.time()
        }
        add_history_entry(history_entry)

        return {
            "status": "success",
            "book_title": req.book_title,
            "mp3_url": stitch_result["mp3"],
            "m4a_url": stitch_result["m4a"],
            "total_chunks": len(resolved_paths),
            "metadata": history_entry
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audiobook stitching failed: {str(e)}")
