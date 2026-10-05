import time
import httpx

def test_endpoints():
    print("Testing /api/voices...")
    r = httpx.get("http://127.0.0.1:8000/api/voices")
    print("Status:", r.status_code, "Count:", len(r.json()))

    print("\nTesting /api/voices/preview for Christopher...")
    t0 = time.time()
    r = httpx.post("http://127.0.0.1:8000/api/voices/preview", json={
        "voice_id": "en-US-ChristopherNeural",
        "sample_text": "Hello! I am Christopher, ready to narrate your text in SPRACH."
    }, timeout=15.0)
    t1 = time.time()
    print(f"Christopher Preview took {t1-t0:.3f}s, status: {r.status_code}")
    print("Response:", r.json())

    print("\nTesting /api/tts/quick with Jenny...")
    t0 = time.time()
    r = httpx.post("http://127.0.0.1:8000/api/tts/quick", json={
        "text": "Welcome to SPRACH! High speed neural speech with zero latency.",
        "voice_id": "en-US-JennyNeural"
    }, timeout=15.0)
    t1 = time.time()
    print(f"Quick Speech took {t1-t0:.3f}s, status: {r.status_code}")
    print("Response:", r.json().get("status"), r.json().get("audio_url"))

    print("\nTesting /api/settings/verify...")
    r = httpx.get("http://127.0.0.1:8000/api/settings/verify")
    print("Verify status:", r.status_code, r.json())

if __name__ == "__main__":
    test_endpoints()
