import os
import subprocess
import tempfile
import wave
import uuid
from pathlib import Path
from typing import List, Dict, Optional
from app.config import AUDIO_OUTPUT_DIR

def pcm_to_wav_bytes(pcm_bytes: bytes, sample_rate: int = 24000, channels: int = 1, sample_width: int = 2) -> bytes:
    """Wraps raw 16-bit PCM bytes into standard WAV format if not already WAV."""
    if pcm_bytes.startswith(b"RIFF"):
        return pcm_bytes
    
    import io
    wav_io = io.BytesIO()
    with wave.open(wav_io, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)
    return wav_io.getvalue()

def convert_audio(
    input_path: Path,
    output_format: str = "mp3",
    bitrate: str = "192k"
) -> Path:
    """Converts an audio file to mp3, m4a, or wav using ffmpeg."""
    output_format = output_format.lower()
    if output_format not in ["mp3", "m4a", "wav"]:
        output_format = "mp3"

    output_filename = f"{input_path.stem}.{output_format}"
    output_path = input_path.parent / output_filename

    # If it's already in the target format and exists
    if input_path.suffix.lower() == f".{output_format}" and output_path.exists():
        return output_path

    cmd = ["ffmpeg", "-y", "-i", str(input_path)]
    if output_format == "mp3":
        cmd.extend(["-c:a", "libmp3lame", "-b:a", bitrate, str(output_path)])
    elif output_format == "m4a":
        cmd.extend(["-c:a", "aac", "-b:a", bitrate, str(output_path)])
    elif output_format == "wav":
        cmd.extend(["-c:a", "pcm_s16le", str(output_path)])

    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg conversion failed: {res.stderr}")

    return output_path

def save_and_transcode(
    raw_audio_bytes: bytes,
    base_name: Optional[str] = None,
    preferred_format: str = "mp3"
) -> Dict[str, str]:
    """
    Saves audio bytes (WAV or raw PCM) and generates MP3, M4A, and WAV versions.
    Returns dictionary with paths and filenames.
    """
    if not base_name:
        base_name = f"tts_{uuid.uuid4().hex[:10]}"

    wav_bytes = pcm_to_wav_bytes(raw_audio_bytes)
    wav_path = AUDIO_OUTPUT_DIR / f"{base_name}.wav"
    with open(wav_path, "wb") as f:
        f.write(wav_bytes)

    # Convert to MP3
    mp3_path = convert_audio(wav_path, "mp3")
    # Convert to M4A
    m4a_path = convert_audio(wav_path, "m4a")

    return {
        "base_name": base_name,
        "wav": f"/audio/{wav_path.name}",
        "mp3": f"/audio/{mp3_path.name}",
        "m4a": f"/audio/{m4a_path.name}",
        "preferred": f"/audio/{base_name}.{preferred_format}",
        "wav_path": str(wav_path),
        "mp3_path": str(mp3_path),
        "m4a_path": str(m4a_path)
    }

def stitch_chunks(
    chunk_paths: List[Path],
    book_title: str,
    output_formats: Optional[List[str]] = None
) -> Dict[str, str]:
    """
    Seamlessly concatenates multiple audio chunk files into unified audiobook tracks.
    """
    if output_formats is None:
        output_formats = ["mp3", "m4a"]

    safe_title = "".join(c for c in book_title if c.isalnum() or c in ("-", "_", " ")).strip()
    safe_title = safe_title.replace(" ", "_") or "audiobook"
    out_base_name = f"{safe_title}_{uuid.uuid4().hex[:6]}"

    # Prepare ffmpeg concat manifest
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        concat_file = f.name
        for p in chunk_paths:
            # Escape single quotes for ffmpeg
            esc_path = str(p.resolve()).replace("'", "'\\''")
            f.write(f"file '{esc_path}'\n")

    try:
        results = {"base_name": out_base_name}
        for fmt in output_formats:
            fmt = fmt.lower()
            out_file = AUDIO_OUTPUT_DIR / f"{out_base_name}.{fmt}"
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file
            ]
            if fmt == "mp3":
                cmd.extend(["-c:a", "libmp3lame", "-b:a", "192k", str(out_file)])
            elif fmt == "m4a":
                cmd.extend(["-c:a", "aac", "-b:a", "192k", str(out_file)])
            elif fmt == "wav":
                cmd.extend(["-c:a", "copy", str(out_file)])

            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode != 0:
                raise RuntimeError(f"FFmpeg stitch failed for {fmt}: {res.stderr}")

            results[fmt] = f"/audio/{out_file.name}"
            results[f"{fmt}_path"] = str(out_file)

        return results
    finally:
        if os.path.exists(concat_file):
            try:
                os.remove(concat_file)
            except Exception:
                pass
