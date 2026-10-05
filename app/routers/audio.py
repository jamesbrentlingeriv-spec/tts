import os
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import FileResponse, StreamingResponse
from app.config import AUDIO_OUTPUT_DIR
from app.services.storage import load_history, delete_history_entry

router = APIRouter(tags=["audio"])

@router.get("/audio/{filename}")
async def get_audio_file(filename: str, request: Request):
    """
    Streams audio files with partial content (HTTP Range: bytes=X-Y) support,
    allowing scrubbing and seeking in HTML5 audio players and PWAs.
    """
    # Prevent directory traversal
    clean_name = Path(filename).name
    file_path = AUDIO_OUTPUT_DIR / clean_name

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Audio file not found")

    file_size = file_path.stat().st_size
    range_header = request.headers.get("range")

    # Determine media type
    ext = file_path.suffix.lower()
    media_types = {
        ".mp3": "audio/mpeg",
        ".m4a": "audio/mp4",
        ".wav": "audio/wav",
        ".ogg": "audio/ogg",
        ".aac": "audio/aac"
    }
    media_type = media_types.get(ext, "application/octet-stream")

    if not range_header:
        return FileResponse(
            path=file_path,
            media_type=media_type,
            headers={
                "Accept-Ranges": "bytes",
                "Content-Length": str(file_size),
                "Content-Disposition": f'inline; filename="{clean_name}"'
            }
        )

    # Parse byte range (e.g. "bytes=0-1024")
    try:
        range_val = range_header.replace("bytes=", "")
        parts = range_val.split("-")
        start = int(parts[0]) if parts[0] else 0
        end = int(parts[1]) if len(parts) > 1 and parts[1] else file_size - 1
        end = min(end, file_size - 1)
        length = end - start + 1

        def iterfile():
            with open(file_path, "rb") as f:
                f.seek(start)
                bytes_left = length
                while bytes_left > 0:
                    chunk_size = min(64 * 1024, bytes_left)
                    data = f.read(chunk_size)
                    if not data:
                        break
                    bytes_left -= len(data)
                    yield data

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(length),
            "Content-Disposition": f'inline; filename="{clean_name}"'
        }
        return StreamingResponse(iterfile(), status_code=206, media_type=media_type, headers=headers)
    except Exception:
        return FileResponse(file_path, media_type=media_type)

@router.get("/api/history")
def get_library_history():
    return load_history()

@router.delete("/api/history/{entry_id}")
def remove_history_entry(entry_id: str):
    success = delete_history_entry(entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"status": "success"}
