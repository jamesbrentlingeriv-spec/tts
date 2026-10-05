// Voice Studio: Dual-Engine Voice Catalog Explorer & Bookmark Manager

const voiceCatalogGrid = document.getElementById("voice-catalog-grid");
const voiceFilterChips = document.getElementById("voice-filter-chips");
const voiceEngineFilterBar = document.getElementById("voice-engine-filter-bar");
let activeVoiceFilter = "all";
let activeEngineFilter = "all";

// Engine Tabs (All, Kokoro, Neural)
if (voiceEngineFilterBar) {
  voiceEngineFilterBar.querySelectorAll(".engine-tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      voiceEngineFilterBar.querySelectorAll(".engine-tab-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      activeEngineFilter = btn.dataset.engineFilter || "all";
      window.renderVoiceCatalog(cachedVoices);
    });
  });
}

// Sub-Language / Accent Filter Chips
if (voiceFilterChips) {
  voiceFilterChips.querySelectorAll(".chip-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      voiceFilterChips.querySelectorAll(".chip-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      activeVoiceFilter = btn.dataset.filter;
      window.renderVoiceCatalog(cachedVoices);
    });
  });
}

window.renderVoiceCatalog = async function(voices) {
  if (!voices || voices.length === 0) {
    if (cachedVoices && cachedVoices.length > 0) {
      voices = cachedVoices;
    } else {
      try {
        const res = await fetch("/api/voices?engine=all");
        cachedVoices = await res.json();
        voices = cachedVoices;
      } catch (err) {
        voices = [];
      }
    }
  }
  if (!voiceCatalogGrid) return;

  voiceCatalogGrid.innerHTML = "";

  const filtered = voices.filter(v => {
    const isGemini = v.category === "gemini" || v.provider === "gemini";
    const isKokoro = v.category === "kokoro" || v.provider === "openrouter";
    const isNeural = !isGemini && !isKokoro;

    if (activeEngineFilter === "gemini" && !isGemini) return false;
    if (activeEngineFilter === "kokoro" && !isKokoro) return false;
    if (activeEngineFilter === "neural" && !isNeural) return false;

    if (activeVoiceFilter === "en-us") return v.language === "en-US";
    if (activeVoiceFilter === "en-gb") return v.language === "en-GB";
    if (activeVoiceFilter === "other") return ["en-AU", "en-CA", "en-IN"].includes(v.language);
    if (activeVoiceFilter === "intl") return !v.language.startsWith("en-");
    if (activeVoiceFilter === "custom") return v.is_custom || v.category === "custom";
    return true;
  });

  if (filtered.length === 0) {
    voiceCatalogGrid.innerHTML = "<div style='color: var(--text-muted); grid-column: 1 / -1; padding: 2rem; text-align: center;'>No voices found matching this filter. Try selecting 'All Voices'.</div>";
    return;
  }

  filtered.forEach(v => {
    const card = document.createElement("div");
    card.className = "voice-card";
    const isCustom = v.is_custom || v.category === "custom";
    const isGemini = v.category === "gemini" || v.provider === "gemini";
    const isKokoro = v.category === "kokoro" || v.provider === "openrouter";

    let badgeText = v.accent || v.language_name || "Voice";
    if (isCustom) badgeText = "⭐ Favorite";
    else if (v.id === "en-US-ChristopherNeural" || v.id === "en-US-JennyNeural" || v.id === "af_heart" || v.id === "Puck" || v.is_flagship) badgeText = "👑 Flagship";

    let engineTag = "";
    if (isGemini) {
      engineTag = `<span class="voice-badge" style="background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3);">✨ Gemini</span>`;
    } else if (isKokoro) {
      engineTag = `<span class="voice-badge" style="background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3);">🍃 Kokoro</span>`;
    } else {
      engineTag = `<span class="voice-badge" style="background: rgba(16, 185, 129, 0.15); color: var(--success); border: 1px solid rgba(16, 185, 129, 0.3);">🎙️ Neural</span>`;
    }

    const tagsHtml = (v.tags || []).map(t => `<span class="tag-pill">${escapeHtml(t)}</span>`).join("");

    card.innerHTML = `
      <div class="voice-card-header">
        <div class="voice-card-name">
          <span>${escapeHtml(v.name)}</span>
          <span style="font-size: 0.75rem; color: var(--text-muted); font-weight: normal;">(${escapeHtml(v.gender || "Voice")})</span>
        </div>
        <div style="display: flex; gap: 0.35rem; align-items: center;">
          ${engineTag}
          <span class="voice-badge ${isCustom ? "custom" : ""}">${badgeText}</span>
        </div>
      </div>
      <div class="voice-card-desc">
        ${escapeHtml(v.description || `${v.accent || "Standard"} tone for speech and narration.`)}
      </div>
      <div class="voice-card-tags">
        ${tagsHtml}
      </div>
      <div class="voice-card-actions">
        <button class="btn btn-secondary btn-sm btn-preview-voice">
          🔊 Preview Voice
        </button>
        <div style="display: flex; gap: 0.4rem;">
          <button class="btn btn-primary btn-sm btn-select-voice">
            Select
          </button>
          ${isCustom ? `<button class="ctrl-btn btn-del-custom" title="Delete custom voice">🗑️</button>` : ""}
        </div>
      </div>
    `;

    // Preview voice sample (cached instantly on disk)
    card.querySelector(".btn-preview-voice").addEventListener("click", async (e) => {
      e.stopPropagation();
      const btn = e.currentTarget;
      btn.disabled = true;
      const originalText = btn.textContent;
      btn.textContent = "🔊 Loading...";

      try {
        const res = await fetch("/api/voices/preview", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            voice_id: v.id,
            sample_text: `Hello! I am ${v.name}, ready to narrate your stories, articles, and audiobooks in SPRACH.`
          })
        });

        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.detail || "Preview failed");
        }

        const data = await res.json();
        const engineLabel = isGemini ? "Google Gemini" : (isKokoro ? "Kokoro 82M" : "Microsoft Neural");
        window.playAudioTrack({
          url: data.audio_url,
          title: `Voice Audition: ${v.name}`,
          subtitle: `${v.gender || "Voice"} • ${engineLabel}`,
          mp3Url: data.mp3_url,
          m4aUrl: data.m4a_url
        });

      } catch (err) {
        alert("Failed to audition voice: " + err.message);
      } finally {
        btn.disabled = false;
        btn.textContent = originalText;
      }
    });

    // Select voice button
    card.querySelector(".btn-select-voice").addEventListener("click", () => {
      // Sync quick engine pill to match voice engine
      const quickPills = document.getElementById("quick-engine-pills");
      if (quickPills) {
        const targetEngine = isGemini ? "gemini" : (isKokoro ? "kokoro" : "neural");
        const targetBtn = quickPills.querySelector(`[data-engine-select="${targetEngine}"]`);
        if (targetBtn) targetBtn.click();
      }

      const quickSelect = document.getElementById("quick-voice-select");
      const abSelect = document.getElementById("ab-voice-select");
      if (quickSelect) {
        quickSelect.value = v.id;
        quickSelect.dispatchEvent(new Event("change"));
      }
      if (abSelect) {
        abSelect.value = v.id;
      }
      switchTab("tab-quick");
    });

    // Delete custom voice
    const delBtn = card.querySelector(".btn-del-custom");
    if (delBtn) {
      delBtn.addEventListener("click", async (e) => {
        e.stopPropagation();
        if (confirm(`Remove favorite bookmark "${v.name}"?`)) {
          await fetch(`/api/voices/${v.id}`, { method: "DELETE" });
          loadVoicesEverywhere();
        }
      });
    }

    voiceCatalogGrid.appendChild(card);
  });
};

// Custom Voice Form (Favorites / Custom Bookmarks)
const formCreateVoice = document.getElementById("form-create-voice");
if (formCreateVoice) {
  formCreateVoice.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("cv-name").value.trim();
    const baseVoice = document.getElementById("cv-base-voice").value;
    const prompt = document.getElementById("cv-prompt").value.trim();
    const tagsInput = document.getElementById("cv-tags").value.trim();

    const tags = tagsInput ? tagsInput.split(",").map(t => t.trim()).filter(Boolean) : ["Favorite"];

    const baseVoiceObj = cachedVoices.find(v => v.id === baseVoice);

    const payload = {
      name: name,
      gender: baseVoiceObj ? baseVoiceObj.gender : "Voice",
      base_voice: baseVoice,
      language: baseVoiceObj ? baseVoiceObj.language : "en-US",
      accent: baseVoiceObj ? baseVoiceObj.accent : "American",
      description: prompt || (baseVoiceObj ? baseVoiceObj.description : "Custom voice bookmark"),
      tags: tags
    };

    try {
      const res = await fetch("/api/voices", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Failed to save voice");
      }

      alert("🎉 Saved to your Favorites!");
      formCreateVoice.reset();
      loadVoicesEverywhere();
    } catch (err) {
      alert("Error saving voice: " + err.message);
    }
  });
}

// Test Voice Sandbox in Designer
const btnTestCustom = document.getElementById("btn-test-custom-voice");
if (btnTestCustom) {
  btnTestCustom.addEventListener("click", async () => {
    const baseVoice = document.getElementById("cv-base-voice").value;
    const sampleText = document.getElementById("cv-sample-text").value.trim() || "Hello! This is a test.";

    btnTestCustom.disabled = true;
    btnTestCustom.textContent = "Loading preview...";

    try {
      const res = await fetch("/api/voices/preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          voice_id: baseVoice,
          sample_text: sampleText
        })
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Preview failed");
      }

      const data = await res.json();
      window.playAudioTrack({
        url: data.audio_url,
        title: "Voice Audition",
        subtitle: `Neural ${baseVoice}`,
        mp3Url: data.mp3_url,
        m4aUrl: data.m4a_url
      });

    } catch (err) {
      alert("Audition error: " + err.message);
    } finally {
      btnTestCustom.disabled = false;
      btnTestCustom.textContent = "Preview Voice";
    }
  });
}
