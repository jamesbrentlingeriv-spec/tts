// Audiobook Studio Pipeline Controller

let currentAudiobookProject = {
  title: "",
  chunks: [],
  chapters: [],
  voiceId: "af_heart",
  isGenerating: false,
  isPaused: false,
  completedChunks: 0
};

const abDropZone = document.getElementById("ab-drop-zone");
const abFileInput = document.getElementById("ab-file-input");
const abRawText = document.getElementById("ab-raw-text");
const abTitleInput = document.getElementById("ab-title");
const abVoiceSelect = document.getElementById("ab-voice-select");
const abChunkSizeSelect = document.getElementById("ab-chunk-size");
const btnAbParse = document.getElementById("btn-ab-parse");

const abWorkspace = document.getElementById("ab-workspace");
const abTotalWords = document.getElementById("ab-total-words");
const abTotalChunks = document.getElementById("ab-total-chunks");
const abEstDuration = document.getElementById("ab-est-duration");
const abChaptersCount = document.getElementById("ab-chapters-count");
const abChunksContainer = document.getElementById("ab-chunks-container");

const btnAbStartBatch = document.getElementById("btn-ab-start-batch");
const btnAbPauseBatch = document.getElementById("btn-ab-pause-batch");
const btnAbCancelBatch = document.getElementById("btn-ab-cancel-batch");
const btnAbStitch = document.getElementById("btn-ab-stitch");
const abProgressFill = document.getElementById("ab-progress-fill");
const abProgressText = document.getElementById("ab-progress-text");
const abProgressPercent = document.getElementById("ab-progress-percent");

// File Drag & Drop
if (abDropZone && abFileInput) {
  abDropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    abDropZone.classList.add("dragover");
  });
  abDropZone.addEventListener("dragleave", () => {
    abDropZone.classList.remove("dragover");
  });
  abDropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    abDropZone.classList.remove("dragover");
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      abFileInput.files = e.dataTransfer.files;
      handleSelectedFile(e.dataTransfer.files[0]);
    }
  });

  abFileInput.addEventListener("change", () => {
    if (abFileInput.files && abFileInput.files.length > 0) {
      handleSelectedFile(abFileInput.files[0]);
    }
  });
}

function handleSelectedFile(file) {
  if (abTitleInput && !abTitleInput.value.trim()) {
    const baseName = file.name.replace(/\.[^/.]+$/, "").replace(/[-_]/g, " ");
    abTitleInput.value = baseName.replace(/\b\w/g, l => l.toUpperCase());
  }
  abDropZone.querySelector(".drop-icon").textContent = "✅";
  abDropZone.querySelector("div[style*='font-weight: 600']").textContent = `Selected: ${file.name} (${Math.round(file.size / 1024)} KB)`;
}

// Parse Document
if (btnAbParse) {
  btnAbParse.addEventListener("click", async () => {
    const file = abFileInput.files && abFileInput.files[0];
    const rawText = abRawText ? abRawText.value.trim() : "";
    const chunkSize = abChunkSizeSelect ? parseInt(abChunkSizeSelect.value, 10) : 1000;

    if (!file && !rawText) {
      alert("Please upload a file or paste text to analyze.");
      return;
    }

    btnAbParse.disabled = true;
    btnAbParse.textContent = "Analyzing Document...";

    try {
      const formData = new FormData();
      if (file) formData.append("file", file);
      if (rawText) formData.append("raw_text", rawText);
      formData.append("chunk_size", chunkSize);

      const res = await fetch("/api/tts/parse-document", {
        method: "POST",
        body: formData
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Failed to parse document");
      }

      const data = await res.json();
      currentAudiobookProject.title = (abTitleInput && abTitleInput.value.trim()) || data.title || "Audiobook";
      currentAudiobookProject.chunks = data.chunks.map(c => ({
        ...c,
        status: "pending", // pending | generating | ready | failed
        audio_url: null,
        wav_filename: null
      }));
      currentAudiobookProject.chapters = data.chapters || [];
      currentAudiobookProject.completedChunks = 0;

      // Update UI Metrics
      abTotalWords.textContent = data.total_words.toLocaleString();
      abTotalChunks.textContent = data.chunk_count;
      abEstDuration.textContent = `${data.est_duration_minutes} min`;
      abChaptersCount.textContent = data.chapter_count;

      renderChunksList();
      abWorkspace.style.display = "block";
      updateProgress();

      // Scroll smoothly to workspace
      abWorkspace.scrollIntoView({ behavior: "smooth" });

    } catch (err) {
      alert("Document analysis failed: " + err.message);
    } finally {
      btnAbParse.disabled = false;
      btnAbParse.textContent = "🔍 Analyze & Prepare Chunks";
    }
  });
}

function renderChunksList() {
  if (!abChunksContainer) return;
  abChunksContainer.innerHTML = "";

  currentAudiobookProject.chunks.forEach((chunk, idx) => {
    const row = document.createElement("div");
    row.className = `chunk-row ${chunk.status}`;
    row.id = `chunk-row-${idx}`;

    const statusBadge = chunk.status === "ready" 
      ? '<span class="chunk-status ready">✅ Ready</span>' 
      : chunk.status === "generating" 
        ? '<span class="chunk-status" style="color: var(--accent-cyan);">⏳ Synthesizing...</span>'
        : chunk.status === "failed" 
          ? '<span class="chunk-status" style="color: var(--danger);">⚠️ Failed</span>'
          : '<span class="chunk-status">Pending</span>';

    row.innerHTML = `
      <div class="chunk-info">
        <div class="chunk-title">
          <span>Chunk ${idx + 1} of ${currentAudiobookProject.chunks.length}</span>
          <span style="font-size: 0.72rem; color: var(--text-muted); font-weight: normal;">(${chunk.char_count} chars, ~${chunk.word_count} words)</span>
          ${statusBadge}
        </div>
        <div class="chunk-preview">${escapeHtml(chunk.text)}</div>
      </div>
      <div style="display: flex; gap: 0.5rem; align-items: center;">
        ${chunk.audio_url ? `<button class="btn btn-secondary btn-sm btn-play-chunk">▶️</button>` : ""}
        <button class="btn btn-secondary btn-sm btn-gen-chunk" title="Generate or re-generate this chunk">
          ${chunk.status === "ready" ? "🔄" : "⚡"}
        </button>
      </div>
    `;

    if (chunk.audio_url) {
      row.querySelector(".btn-play-chunk").addEventListener("click", () => {
        window.playAudioTrack({
          url: chunk.audio_url,
          title: `${currentAudiobookProject.title} - Chunk ${idx + 1}`,
          subtitle: "Audiobook Preview",
          mp3Url: chunk.mp3_url || chunk.audio_url,
          m4aUrl: chunk.m4a_url
        });
      });
    }

    row.querySelector(".btn-gen-chunk").addEventListener("click", () => {
      generateSingleChunk(idx);
    });

    abChunksContainer.appendChild(row);
  });
}

async function generateSingleChunk(idx) {
  const chunk = currentAudiobookProject.chunks[idx];
  if (!chunk) return;

  chunk.status = "generating";
  renderChunksList();

  const voiceId = (abVoiceSelect && abVoiceSelect.value) || "af_heart";

  try {
    const res = await fetch("/api/tts/audiobook/generate-chunk", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chunk_id: String(idx),
        text: chunk.text,
        voice_id: voiceId
      })
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Chunk generation failed");
    }

    const data = await res.json();
    chunk.status = "ready";
    chunk.audio_url = data.audio_url;
    chunk.mp3_url = data.mp3_url;
    chunk.m4a_url = data.m4a_url;
    chunk.wav_filename = data.wav_filename;

  } catch (err) {
    chunk.status = "failed";
    console.error(`Chunk ${idx} error:`, err);
  } finally {
    recalcCompleted();
    renderChunksList();
    updateProgress();
  }
}

function recalcCompleted() {
  currentAudiobookProject.completedChunks = currentAudiobookProject.chunks.filter(c => c.status === "ready").length;
  if (btnAbStitch) {
    btnAbStitch.disabled = currentAudiobookProject.completedChunks === 0;
  }
}

function updateProgress() {
  const total = currentAudiobookProject.chunks.length;
  const done = currentAudiobookProject.completedChunks;
  const pct = total > 0 ? Math.round((done / total) * 100) : 0;

  if (abProgressFill) abProgressFill.style.width = `${pct}%`;
  if (abProgressPercent) abProgressPercent.textContent = `${pct}%`;
  if (abProgressText) {
    if (done === total && total > 0) {
      abProgressText.textContent = "All chunks generated! Ready to stitch into master audiobook.";
    } else {
      abProgressText.textContent = `${done} of ${total} chunks completed`;
    }
  }
}

// Batch Generation Runner
if (btnAbStartBatch) {
  btnAbStartBatch.addEventListener("click", async () => {
    if (currentAudiobookProject.isGenerating) return;
    currentAudiobookProject.isGenerating = true;
    currentAudiobookProject.isPaused = false;

    btnAbStartBatch.style.display = "none";
    btnAbPauseBatch.style.display = "inline-flex";
    btnAbCancelBatch.style.display = "inline-flex";

    for (let i = 0; i < currentAudiobookProject.chunks.length; i++) {
      if (!currentAudiobookProject.isGenerating) break;

      // Handle pause loop
      while (currentAudiobookProject.isPaused) {
        await new Promise(r => setTimeout(r, 500));
        if (!currentAudiobookProject.isGenerating) break;
      }
      if (!currentAudiobookProject.isGenerating) break;

      const chunk = currentAudiobookProject.chunks[i];
      if (chunk.status !== "ready") {
        await generateSingleChunk(i);
        // Small delay to be polite to the API rate limit
        await new Promise(r => setTimeout(r, 400));
      }
    }

    currentAudiobookProject.isGenerating = false;
    btnAbStartBatch.style.display = "inline-flex";
    btnAbStartBatch.textContent = "▶️ Resume / Regenerate Remaining";
    btnAbPauseBatch.style.display = "none";
    btnAbCancelBatch.style.display = "none";
  });
}

if (btnAbPauseBatch) {
  btnAbPauseBatch.addEventListener("click", () => {
    currentAudiobookProject.isPaused = !currentAudiobookProject.isPaused;
    btnAbPauseBatch.textContent = currentAudiobookProject.isPaused ? "▶️ Resume" : "⏸️ Pause";
  });
}

if (btnAbCancelBatch) {
  btnAbCancelBatch.addEventListener("click", () => {
    currentAudiobookProject.isGenerating = false;
    currentAudiobookProject.isPaused = false;
    btnAbStartBatch.style.display = "inline-flex";
    btnAbPauseBatch.style.display = "none";
    btnAbCancelBatch.style.display = "none";
  });
}

// Stitch Master Audiobook
if (btnAbStitch) {
  btnAbStitch.addEventListener("click", async () => {
    const readyChunks = currentAudiobookProject.chunks.filter(c => c.status === "ready" && c.audio_url);
    if (readyChunks.length === 0) {
      alert("No completed audio chunks to stitch!");
      return;
    }

    btnAbStitch.disabled = true;
    btnAbStitch.textContent = "⏳ Stitching with FFmpeg...";

    const chunkFiles = readyChunks.map(c => c.wav_filename || c.audio_url);
    const bookTitle = (abTitleInput && abTitleInput.value.trim()) || currentAudiobookProject.title || "My Audiobook";

    try {
      const res = await fetch("/api/tts/audiobook/stitch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          book_title: bookTitle,
          chunk_files: chunkFiles,
          voice_name: (abVoiceSelect && abVoiceSelect.options[abVoiceSelect.selectedIndex]?.text) || "Narrator Voice"
        })
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Stitching failed");
      }

      const data = await res.json();

      // Launch full audiobook in player
      window.playAudioTrack({
        url: data.mp3_url,
        title: `📚 ${bookTitle}`,
        subtitle: `Complete Audiobook • ${data.chunks_stitched} Chunks`,
        mp3Url: data.mp3_url,
        m4aUrl: data.m4a_url
      });

      alert(`🎉 Master Audiobook stitched successfully!\nDownloaded/playable in both MP3 and M4A formats.`);

    } catch (err) {
      alert("Stitching failed: " + err.message);
    } finally {
      btnAbStitch.disabled = false;
      btnAbStitch.textContent = "🎉 Stitch Master Audiobook (MP3 & M4A)";
    }
  });
}
