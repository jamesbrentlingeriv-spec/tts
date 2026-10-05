import uvicorn
import webbrowser
import sys
import time
import threading

def open_browser():
    time.sleep(1.2)
    webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    print("=" * 60)
    print("🎙️ SPRACH - Neural & Kokoro TTS Studio & Audiobook Creator (PWA)")
    print("=" * 60)
    print("Starting server at: http://localhost:8000")
    print("Press Ctrl+C to stop.")
    print("=" * 60)

    # Launch browser automatically
    if "--no-browser" not in sys.argv:
        threading.Thread(target=open_browser, daemon=True).start()

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
