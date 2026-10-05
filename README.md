# 🎙️ SPRACH - Neural & Kokoro TTS Studio & Audiobook Creator (PWA)

A high-performance Progressive Web App (PWA) designed for AI Text-to-Speech using **Microsoft Azure Neural TTS** (Free, sub-second latency, zero API keys required) and **Kokoro 82M** (54 expressive voices via OpenRouter API with pre-cached instant previews).

---

## ✨ Features

- **⚡ Instant Speech Generator**:
  - Sub-second speech generation with Microsoft Neural or Kokoro 82M.
  - Interactive one-click presets: *Tell a Joke*, *Movie Trailer*, *Pirate Toast*, *1940s Radio Flash*, *Sarcastic Coffee*, *Lore Master*.
  - Instant playback and one-click download in **MP3** or **M4A**.

- **📚 Audiobook Studio**:
  - Convert full books, chapters, or articles with smart boundary chunking.
  - Drag-and-drop document support: `.txt`, `.md`, `.pdf`, `.epub`.
  - Batch generation runner with live progress bar and individual chunk retry.
  - **FFmpeg Master Stitcher**: Combines all chunks into a unified master `.mp3` or `.m4a` audiobook track.

- **🎨 Dual-Engine Voice Studio**:
  - **Microsoft Neural TTS**: 35 studio-grade broadcast narrators including Christopher, Jenny, Guy, Andrew, Sonia, and Ryan.
  - **Kokoro 82M (OpenRouter)**: 49 expressive multilingual voices across 8 languages (Heart, Bella, Nicole, Michael, Adam, Fenrir, Emma, George, etc.).
  - **100% Pre-Cached Auditions**: Every voice preview is cached on disk for instant (<10ms) playback with zero wait time.

- **📱 Progressive Web App (PWA)**:
  - Custom brand logo, dark red aesthetic, installable on mobile and desktop.

---

## 🚀 Quick Start

```bash
python run.py
```
Open **http://localhost:8000** in your browser.
