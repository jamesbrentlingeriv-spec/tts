// SPRACH - Core Application & Global Audio Player (Kokoro 82M Edition)

// PWA Service Worker Registration
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js")
      .then((reg) => console.log("SPRACH Service Worker Registered:", reg.scope))
      .catch((err) => console.error("Service Worker Registration Failed:", err));
  });
}

// PWA Install Prompt Handling
let deferredInstallPrompt = null;
const installBtn = document.getElementById("btn-install-pwa");

window.addEventListener("beforeinstallprompt", (e) => {
  e.preventDefault();
  deferredInstallPrompt = e;
  if (installBtn) {
    installBtn.style.display = "inline-flex";
  }
});

if (installBtn) {
  installBtn.addEventListener("click", async () => {
    if (!deferredInstallPrompt) return;
    deferredInstallPrompt.prompt();
    const { outcome } = await deferredInstallPrompt.userChoice;
    console.log(`User response to install: ${outcome}`);
    deferredInstallPrompt = null;
    installBtn.style.display = "none";
  });
}

window.addEventListener("appinstalled", () => {
  console.log("SPRACH PWA installed successfully");
  if (installBtn) installBtn.style.display = "none";
});

// Tab Navigation
const navButtons = document.querySelectorAll(".nav-btn");
const tabPanes = document.querySelectorAll(".tab-pane");

function switchTab(tabId) {
  navButtons.forEach(btn => {
    btn.classList.toggle("active", btn.dataset.tab === tabId);
  });
  tabPanes.forEach(pane => {
    pane.classList.toggle("active", pane.id === tabId);
  });
  if (tabId === "tab-library") {
    loadAudioLibrary();
  }
  if (tabId === "tab-voices") {
    if (window.renderVoiceCatalog) window.renderVoiceCatalog();
  }
}

navButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    const target = btn.dataset.tab;
    switchTab(target);
    window.location.hash = target.replace("tab-", "");
  });
});

// Handle direct hash navigation
window.addEventListener("DOMContentLoaded", () => {
  const cleanHash = window.location.hash.replace("#", "");
  if (cleanHash) {
    const targetId = cleanHash.startsWith("tab-") ? cleanHash : `tab-${cleanHash}`;
    if (document.getElementById(targetId)) {
      switchTab(targetId);
    }
  }
  checkSettingsStatus();
  loadVoicesEverywhere();
});

// Global Audio Player
const audioElement = document.getElementById("global-audio-element");
const playerBar = document.getElementById("app-player");
const playerTitle = document.getElementById("player-title");
const playerSubtitle = document.getElementById("player-subtitle");
const playerPlayBtn = document.getElementById("player-play-btn");
const playerScrubber = document.getElementById("player-scrubber");
const playerCurrentTime = document.getElementById("player-current-time");
const playerDuration = document.getElementById("player-duration");
const playerRw10 = document.getElementById("player-rw10");
const playerFf10 = document.getElementById("player-ff10");
const playerSpeedBtn = document.getElementById("player-speed-btn");
const playerDlMp3 = document.getElementById("player-dl-mp3");
const playerDlM4a = document.getElementById("player-dl-m4a");

const speeds = [1.0, 1.25, 1.5, 2.0, 0.75];
let currentSpeedIndex = 0;

function formatTime(secs) {
  if (isNaN(secs)) return "0:00";
  const m = Math.floor(secs / 60);
  const s = Math.floor(secs % 60);
  return `${m}:${s < 10 ? "0" : ""}${s}`;
}

window.playAudioTrack = function(track) {
  if (!audioElement) return;

  playerTitle.textContent = track.title || "Audio Playback";
  playerSubtitle.textContent = track.subtitle || "Kokoro 82M";

  if (track.mp3Url) {
    playerDlMp3.href = track.mp3Url;
    playerDlMp3.download = `${track.title || "audio"}.mp3`;
    playerDlMp3.style.display = "inline-flex";
  } else {
    playerDlMp3.style.display = "none";
  }

  if (track.m4aUrl) {
    playerDlM4a.href = track.m4aUrl;
    playerDlM4a.download = `${track.title || "audio"}.m4a`;
    playerDlM4a.style.display = "inline-flex";
  } else {
    playerDlM4a.style.display = "none";
  }

  audioElement.src = track.url;
  audioElement.playbackRate = speeds[currentSpeedIndex];
  audioElement.play()
    .then(() => {
      playerPlayBtn.textContent = "⏸️";
      playerBar.classList.add("playing");
    })
    .catch((err) => console.error("Playback error:", err));
};

if (playerPlayBtn) {
  playerPlayBtn.addEventListener("click", () => {
    if (!audioElement.src) return;
    if (audioElement.paused) {
      audioElement.play();
      playerPlayBtn.textContent = "⏸️";
    } else {
      audioElement.pause();
      playerPlayBtn.textContent = "▶️";
    }
  });
}

if (audioElement) {
  audioElement.addEventListener("timeupdate", () => {
    if (!isNaN(audioElement.duration)) {
      const progress = (audioElement.currentTime / audioElement.duration) * 100;
      playerScrubber.value = progress || 0;
      playerCurrentTime.textContent = formatTime(audioElement.currentTime);
      playerDuration.textContent = formatTime(audioElement.duration);
    }
  });

  audioElement.addEventListener("ended", () => {
    playerPlayBtn.textContent = "▶️";
  });
}

if (playerScrubber) {
  playerScrubber.addEventListener("input", (e) => {
    if (!audioElement.duration) return;
    const seekTo = (e.target.value / 100) * audioElement.duration;
    audioElement.currentTime = seekTo;
  });
}

if (playerRw10) {
  playerRw10.addEventListener("click", () => {
    if (!audioElement.src) return;
    audioElement.currentTime = Math.max(0, audioElement.currentTime - 10);
  });
}

if (playerFf10) {
  playerFf10.addEventListener("click", () => {
    if (!audioElement.src) return;
    audioElement.currentTime = Math.min(audioElement.duration || 0, audioElement.currentTime + 10);
  });
}

if (playerSpeedBtn) {
  playerSpeedBtn.addEventListener("click", () => {
    currentSpeedIndex = (currentSpeedIndex + 1) % speeds.length;
    const newSpeed = speeds[currentSpeedIndex];
    audioElement.playbackRate = newSpeed;
    playerSpeedBtn.textContent = `${newSpeed}x`;
  });
}

// Settings & Engine Verification
async function checkSettingsStatus() {
  const badge = document.getElementById("status-kokoro-badge");
  const text = document.getElementById("status-text");
  const statusBoxTitle = document.getElementById("settings-status-title");
  const statusBoxDesc = document.getElementById("settings-status-desc");
  const statusBox = document.getElementById("engine-status-box");
  const kokoroBox = document.getElementById("kokoro-api-box");
  const geminiBox = document.getElementById("gemini-api-box");
  const keySavedBadge = document.getElementById("key-saved-badge");
  const geminiKeySavedBadge = document.getElementById("gemini-key-saved-badge");
  const keyInput = document.getElementById("set-openrouter-key");
  const geminiKeyInput = document.getElementById("set-gemini-key");

  const radioNeural = document.getElementById("radio-engine-neural");
  const radioKokoro = document.getElementById("radio-engine-kokoro");
  const radioGemini = document.getElementById("radio-engine-gemini");
  const cardNeural = document.getElementById("engine-card-neural");
  const cardKokoro = document.getElementById("engine-card-kokoro");
  const cardGemini = document.getElementById("engine-card-gemini");

  try {
    const res = await fetch("/api/settings");
    const data = await res.json();
    const isKokoro = data.engine === "kokoro";
    const isGemini = data.engine === "gemini";
    const isNeural = !isKokoro && !isGemini;

    // Set radios and cards
    if (radioNeural && radioKokoro && radioGemini) {
      radioNeural.checked = isNeural;
      radioKokoro.checked = isKokoro;
      radioGemini.checked = isGemini;
    }

    [
      { card: cardNeural, active: isNeural },
      { card: cardKokoro, active: isKokoro },
      { card: cardGemini, active: isGemini }
    ].forEach(({ card, active }) => {
      if (card) {
        card.style.borderColor = active ? "var(--accent-red)" : "var(--border-color)";
        card.style.borderWidth = active ? "2px" : "1px";
      }
    });

    // API key sections
    if (kokoroBox) kokoroBox.style.display = isKokoro ? "block" : "none";
    if (geminiBox) geminiBox.style.display = isGemini ? "block" : "none";

    if (keySavedBadge) keySavedBadge.style.display = data.has_openrouter_key ? "inline" : "none";
    if (keyInput) {
      if (data.has_openrouter_key && data.masked_openrouter_key) {
        keyInput.placeholder = data.masked_openrouter_key;
      } else {
        keyInput.placeholder = "sk-or-v1-...";
        keyInput.value = "";
      }
    }

    if (geminiKeySavedBadge) geminiKeySavedBadge.style.display = data.has_gemini_key ? "inline" : "none";
    if (geminiKeyInput) {
      if (data.has_gemini_key && data.masked_gemini_key) {
        geminiKeyInput.placeholder = data.masked_gemini_key;
      } else {
        geminiKeyInput.placeholder = "AIzaSy... (from Google AI Studio)";
        geminiKeyInput.value = "";
      }
    }

    // Status box in settings
    if (statusBoxTitle && statusBoxDesc) {
      if (isGemini) {
        statusBoxTitle.textContent = "Google Gemini 2.0 Flash Active";
        statusBoxDesc.textContent = "5 Native Studio Voices • Puck & Charon Flagships • Expressive Audio Generation";
        if (statusBox) {
          statusBox.style.background = "rgba(59, 130, 246, 0.08)";
          statusBox.style.borderColor = "rgba(59, 130, 246, 0.25)";
        }
      } else if (isKokoro) {
        statusBoxTitle.textContent = "Kokoro 82M Active (OpenRouter)";
        statusBoxDesc.textContent = "54 Expressive Voices across 8 Languages • Previews Cached to Disk";
        if (statusBox) {
          statusBox.style.background = "rgba(239, 68, 68, 0.08)";
          statusBox.style.borderColor = "rgba(239, 68, 68, 0.25)";
        }
      } else {
        statusBoxTitle.textContent = "Microsoft Neural Engine Active (Free)";
        statusBoxDesc.textContent = "Latency: ~0.8s • Studio broadcast quality • 100% Free • No API Key";
        if (statusBox) {
          statusBox.style.background = "rgba(16, 185, 129, 0.08)";
          statusBox.style.borderColor = "rgba(16, 185, 129, 0.25)";
        }
      }
    }

    // Header badge
    if (badge && text) {
      badge.classList.remove("warning");
      const dot = badge.querySelector(".dot");
      if (isGemini) {
        text.textContent = "Gemini Active";
        badge.title = "Google Gemini 2.0 Flash Audio is active";
        if (dot) dot.style.background = "#60a5fa";
      } else if (isKokoro) {
        text.textContent = "Kokoro Active";
        badge.title = "Kokoro 82M TTS via OpenRouter is active";
        if (dot) dot.style.background = "var(--accent-red)";
      } else {
        text.textContent = "Neural Ready (Free)";
        badge.title = "Microsoft Neural TTS is active and ready";
        if (dot) dot.style.background = "var(--success)";
      }
    }

    const headerSubtext = document.getElementById("header-engine-subtext");
    if (headerSubtext) {
      headerSubtext.textContent = isGemini ? "Google Gemini 2.0 Flash" : (isKokoro ? "Kokoro 82M TTS" : "Microsoft Neural TTS");
    }

    const catTitle = document.getElementById("catalog-title");
    const catSubtitle = document.getElementById("catalog-subtitle");
    if (catTitle && catSubtitle) {
      if (isGemini) {
        catTitle.textContent = "🎨 Gemini Voice Catalog";
        catSubtitle.textContent = "5 Expressive Google Gemini audio voices (Puck, Charon, Kore, Fenrir, Aoede).";
      } else if (isKokoro) {
        catTitle.textContent = "🎨 Kokoro 82M Voice Catalog";
        catSubtitle.textContent = "54 Expressive multilingual voices powered by OpenRouter. Previews cached to disk.";
      } else {
        catTitle.textContent = "🎨 Microsoft Neural Voice Catalog";
        catSubtitle.textContent = "Studio-quality neural voices across multiple accents. 100% Free, unlimited, ~0.8s generation.";
      }
    }

    const quickSub = document.getElementById("quick-card-subtitle");
    const quickVLabel = document.getElementById("quick-voice-label");
    if (quickSub) {
      quickSub.textContent = isGemini
        ? "Gemini 2.0 Flash Audio with expressive native voices Puck, Charon, Kore, & more."
        : (isKokoro
            ? "54 Expressive Kokoro-82M voices powered by OpenRouter API. Previews are cached."
            : "Lightning-fast speech with Microsoft Azure Neural voices (Free & Unlimited, ~0.8s).");
    }
    if (quickVLabel) {
      quickVLabel.textContent = isGemini ? "Voice (Gemini)" : (isKokoro ? "Voice (Kokoro 82M)" : "Voice (Microsoft Neural)");
    }

    const fSelect = document.getElementById("set-default-format");
    if (fSelect && data.default_format) fSelect.value = data.default_format;

    // Sync pill buttons on Quick & Audiobook tabs
    const targetEngine = isGemini ? "gemini" : (isKokoro ? "kokoro" : "neural");
    currentQuickEngine = targetEngine;
    currentAbEngine = targetEngine;

    ["quick", "ab"].forEach(prefix => {
      const pills = document.getElementById(`${prefix}-engine-pills`);
      if (pills) {
        pills.querySelectorAll("button").forEach(b => {
          b.classList.toggle("active", b.dataset.engineSelect === targetEngine);
        });
      }
      const selectElem = document.getElementById(`${prefix === "quick" ? "quick" : "ab"}-voice-select`);
      if (selectElem && cachedVoices && cachedVoices.length > 0) {
        populateSingleVoiceSelect(selectElem, cachedVoices, targetEngine);
      }
    });

  } catch (err) {
    console.error("Failed to load settings:", err);
  }
}

// Instant Engine Saver
async function saveEngineDirectly(engineName) {
  try {
    const res = await fetch("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ engine: engineName })
    });
    if (res.ok) {
      await checkSettingsStatus();
      await loadVoicesEverywhere();
    }
  } catch (err) {
    console.error("Error setting engine:", err);
  }
}

// Global Engine & Pill State
let currentQuickEngine = "all";
let currentAbEngine = "all";

// Setup interactive engine pills & card click handlers
document.addEventListener("DOMContentLoaded", () => {
  const radioNeural = document.getElementById("radio-engine-neural");
  const radioKokoro = document.getElementById("radio-engine-kokoro");
  const radioGemini = document.getElementById("radio-engine-gemini");
  const cardNeural = document.getElementById("engine-card-neural");
  const cardKokoro = document.getElementById("engine-card-kokoro");
  const cardGemini = document.getElementById("engine-card-gemini");
  const kokoroBox = document.getElementById("kokoro-api-box");
  const geminiBox = document.getElementById("gemini-api-box");

  function setCardActive(activeCard, radio) {
    if (radio) radio.checked = true;
    [cardNeural, cardKokoro, cardGemini].forEach(c => {
      if (c) {
        c.style.borderColor = (c === activeCard) ? "var(--accent-red)" : "var(--border-color)";
        c.style.borderWidth = (c === activeCard) ? "2px" : "1px";
      }
    });
  }

  if (cardNeural) {
    cardNeural.addEventListener("click", async () => {
      setCardActive(cardNeural, radioNeural);
      if (kokoroBox) kokoroBox.style.display = "none";
      if (geminiBox) geminiBox.style.display = "none";
      await saveEngineDirectly("microsoft_neural");
    });
  }

  if (cardKokoro) {
    cardKokoro.addEventListener("click", async () => {
      setCardActive(cardKokoro, radioKokoro);
      if (kokoroBox) kokoroBox.style.display = "block";
      if (geminiBox) geminiBox.style.display = "none";
      await saveEngineDirectly("kokoro");
    });
  }

  if (cardGemini) {
    cardGemini.addEventListener("click", async () => {
      setCardActive(cardGemini, radioGemini);
      if (kokoroBox) kokoroBox.style.display = "none";
      if (geminiBox) geminiBox.style.display = "block";
      await saveEngineDirectly("gemini");
    });
  }

  // Quick and Audiobook Engine Pills
  ["quick", "ab"].forEach(prefix => {
    const pills = document.getElementById(`${prefix}-engine-pills`);
    if (pills) {
      pills.querySelectorAll("button").forEach(btn => {
        btn.addEventListener("click", () => {
          pills.querySelectorAll("button").forEach(b => b.classList.remove("active"));
          btn.classList.add("active");
          const selected = btn.dataset.engineSelect;
          const selectElem = document.getElementById(`${prefix === "quick" ? "quick" : "ab"}-voice-select`);
          if (prefix === "quick") {
            currentQuickEngine = selected;
            populateSingleVoiceSelect(selectElem, cachedVoices, selected);
          } else {
            currentAbEngine = selected;
            populateSingleVoiceSelect(selectElem, cachedVoices, selected);
          }
        });
      });
    }
  });
});

// Settings Form Submission
const settingsForm = document.getElementById("form-settings");
if (settingsForm) {
  settingsForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const isGemini = document.getElementById("radio-engine-gemini")?.checked;
    const isKokoro = document.getElementById("radio-engine-kokoro")?.checked;
    const selectedEngine = isGemini ? "gemini" : (isKokoro ? "kokoro" : "microsoft_neural");
    const openrouterKey = document.getElementById("set-openrouter-key")?.value?.trim() || undefined;
    const geminiKey = document.getElementById("set-gemini-key")?.value?.trim() || undefined;
    const format = document.getElementById("set-default-format")?.value || "mp3";

    const payload = {
      engine: selectedEngine,
      default_format: format
    };
    if (openrouterKey) {
      payload.openrouter_api_key = openrouterKey;
    }
    if (geminiKey) {
      payload.gemini_api_key = geminiKey;
    }

    try {
      const res = await fetch("/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const engineLabel = isGemini ? "Google Gemini 2.0 Flash" : (isKokoro ? "Kokoro 82M (OpenRouter)" : "Microsoft Neural (Free)");
        alert(`✅ Settings saved! Active Engine: ${engineLabel}`);
        await checkSettingsStatus();
        await loadVoicesEverywhere();
      } else {
        alert("Failed to save settings.");
      }
    } catch (err) {
      alert("Error saving settings: " + err.message);
    }
  });
}

// Test Connection Button
const testConnBtn = document.getElementById("btn-test-connection");
if (testConnBtn) {
  testConnBtn.addEventListener("click", async () => {
    testConnBtn.disabled = true;
    testConnBtn.textContent = "🧪 Testing...";
    try {
      const res = await fetch("/api/settings/verify");
      const data = await res.json();
      if (data.valid) {
        let msg = "";
        if (data.engine === "gemini") {
          msg = `🎉 Google Gemini Connected!\nSpeed: ${data.latency_ms}ms\nStatus: Active & Validated (Gemini 2.0 Flash Audio)`;
        } else if (data.engine === "kokoro") {
          msg = `🎉 Kokoro 82M Connected via OpenRouter!\nSpeed: ${data.latency_ms}ms\nProvider: ${data.provider}`;
        } else {
          msg = `🎉 Microsoft Neural Connected!\nSpeed: ${data.latency_ms}ms\nStatus: 100% Free & Unlimited`;
        }
        alert(msg);
        checkSettingsStatus();
      } else {
        alert("⚠️ Engine connection issue: " + (data.error || "Unknown"));
      }
    } catch (err) {
      alert("Error verifying connection: " + err.message);
    } finally {
      testConnBtn.disabled = false;
      testConnBtn.textContent = "🧪 Test Active Engine";
    }
  });
}

// Clear / Block API Key Buttons
const btnClearOrKey = document.getElementById("btn-clear-openrouter-key");
if (btnClearOrKey) {
  btnClearOrKey.addEventListener("click", async () => {
    if (!confirm("Are you sure you want to block and remove the saved OpenRouter API key?")) return;
    try {
      const res = await fetch("/api/settings/clear-key", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key_name: "openrouter" })
      });
      if (res.ok) {
        alert("🚫 OpenRouter API key blocked and deleted from configuration.");
        await checkSettingsStatus();
      } else {
        alert("Failed to clear key.");
      }
    } catch (err) {
      alert("Error: " + err.message);
    }
  });
}

const btnClearGemKey = document.getElementById("btn-clear-gemini-key");
if (btnClearGemKey) {
  btnClearGemKey.addEventListener("click", async () => {
    if (!confirm("Are you sure you want to block and remove the saved Google Gemini API key?")) return;
    try {
      const res = await fetch("/api/settings/clear-key", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key_name: "gemini" })
      });
      if (res.ok) {
        alert("🚫 Google Gemini API key blocked and deleted from configuration.");
        await checkSettingsStatus();
      } else {
        alert("Failed to clear key.");
      }
    } catch (err) {
      alert("Error: " + err.message);
    }
  });
}

// Global Voice Loader
let cachedVoices = [];
async function loadVoicesEverywhere() {
  try {
    const res = await fetch("/api/voices?engine=all");
    cachedVoices = await res.json();
    populateVoiceSelects(cachedVoices);
    if (window.renderVoiceCatalog) {
      window.renderVoiceCatalog(cachedVoices);
    }
  } catch (err) {
    console.error("Error loading voices:", err);
  }
}

function populateSingleVoiceSelect(select, voices, engineFilter = "all") {
  if (!select) return;
  const currentVal = select.value;
  select.innerHTML = "";

  const filteredVoices = voices.filter(v => {
    const isGemini = v.category === "gemini" || v.provider === "gemini";
    const isKokoro = v.category === "kokoro" || v.provider === "openrouter";
    const isNeural = !isGemini && !isKokoro;

    if (engineFilter === "gemini" && !isGemini) return false;
    if (engineFilter === "kokoro" && !isKokoro) return false;
    if (engineFilter === "neural" && !isNeural) return false;
    return true;
  });

  const groupMap = {
    "en-US": "🇺🇸 US English",
    "en-GB": "🇬🇧 British English",
    "en-AU": "🇦🇺 Australian",
    "en-CA": "🇨🇦 Canadian",
    "en-IN": "🇮🇳 Indian English",
    "en-SE": "🇪🇺 European English",
    "ja-JP": "🇯🇵 Japanese",
    "zh-CN": "🇨🇳 Mandarin Chinese",
    "es-ES": "🇪🇸 Spanish",
    "fr-FR": "🇫🇷 French",
    "hi-IN": "🇮🇳 Hindi",
    "it-IT": "🇮🇹 Italian",
    "pt-BR": "🇧🇷 Brazilian Portuguese",
    "custom": "⭐ My Favorites & Custom"
  };

  const optgroups = {};
  filteredVoices.forEach(v => {
    const isGemini = v.category === "gemini" || v.provider === "gemini";
    const isKokoro = v.category === "kokoro" || v.provider === "openrouter";
    const enginePrefix = isGemini ? "✨ Gemini" : (isKokoro ? "🍃 Kokoro" : "🎙️ Neural");
    const langKey = v.language || "en-US";
    const langLabel = groupMap[langKey] || langKey;
    const groupKey = engineFilter === "all" ? `${enginePrefix} • ${langLabel}` : langLabel;

    if (!optgroups[groupKey]) {
      optgroups[groupKey] = document.createElement("optgroup");
      optgroups[groupKey].label = groupKey;
    }

    const opt = document.createElement("option");
    opt.value = v.id;
    opt.textContent = `${v.name} (${v.gender || "Voice"}${v.accent ? `, ${v.accent}` : ""})`;
    optgroups[groupKey].appendChild(opt);
  });

  Object.values(optgroups).forEach(g => {
    if (g.children.length > 0) select.appendChild(g);
  });

  if (currentVal && Array.from(select.options).some(o => o.value === currentVal)) {
    select.value = currentVal;
  } else if (filteredVoices.length > 0) {
    const flagship = filteredVoices.find(v => v.is_flagship) || filteredVoices[0];
    select.value = flagship.id;
  }

  select.dispatchEvent(new Event("change"));
}

function populateVoiceSelects(voices) {
  const quickSelect = document.getElementById("quick-voice-select");
  const abSelect = document.getElementById("ab-voice-select");
  const cvBaseSelect = document.getElementById("cv-base-voice");

  populateSingleVoiceSelect(quickSelect, voices, currentQuickEngine);
  populateSingleVoiceSelect(abSelect, voices, currentAbEngine);

  if (cvBaseSelect) {
    const currentVal = cvBaseSelect.value;
    cvBaseSelect.innerHTML = "";
    voices.filter(v => !v.is_custom).forEach(v => {
      const opt = document.createElement("option");
      opt.value = v.id;
      const isGemini = v.category === "gemini" || v.provider === "gemini";
      const isKokoro = v.category === "kokoro" || v.provider === "openrouter";
      const providerLabel = isGemini ? "Gemini" : (isKokoro ? "Kokoro" : "Neural");
      opt.textContent = `${v.name} (${providerLabel}, ${v.gender || "Voice"})`;
      cvBaseSelect.appendChild(opt);
    });
    if (currentVal) cvBaseSelect.value = currentVal;
  }
}

// History Library
async function loadAudioLibrary() {
  const grid = document.getElementById("history-grid");
  if (!grid) return;
  grid.innerHTML = "<div style='color: var(--text-muted);'>Loading library...</div>";

  try {
    const res = await fetch("/api/history");
    const items = await res.json();
    if (!items || items.length === 0) {
      grid.innerHTML = "<div style='color: var(--text-muted); padding: 1.5rem;'>No generated audio clips yet. Generate something in Quick Speech or Audiobook Studio!</div>";
      return;
    }

    grid.innerHTML = "";
    items.forEach(item => {
      const card = document.createElement("div");
      card.className = "history-card";
      const dateStr = new Date((item.created_at || Date.now() / 1000) * 1000).toLocaleString();
      const typeBadge = item.type === "audiobook" ? "📚 Audiobook" : "⚡ Quick Clip";

      card.innerHTML = `
        <div class="history-card-header">
          <div class="history-title">${escapeHtml(item.title || "Untitled Audio")}</div>
          <span class="voice-badge">${typeBadge}</span>
        </div>
        <div class="history-meta">
          <span>🎙️ ${escapeHtml(item.voice || "Heart")}</span>
          <span>📅 ${dateStr}</span>
        </div>
        <div class="history-card-actions">
          <button class="btn btn-secondary btn-sm btn-play-hist">▶️ Play</button>
          <div style="display: flex; gap: 0.4rem;">
            ${item.mp3_url ? `<a href="${item.mp3_url}" download="${item.title || "audio"}.mp3" class="dl-btn">MP3</a>` : ""}
            ${item.m4a_url ? `<a href="${item.m4a_url}" download="${item.title || "audio"}.m4a" class="dl-btn">M4A</a>` : ""}
            <button class="ctrl-btn btn-del-hist" title="Delete" style="font-size: 0.9rem;">🗑️</button>
          </div>
        </div>
      `;

      card.querySelector(".btn-play-hist").addEventListener("click", () => {
        window.playAudioTrack({
          url: item.mp3_url || item.m4a_url || item.wav_url,
          title: item.title,
          subtitle: `${item.voice} • ${typeBadge}`,
          mp3Url: item.mp3_url,
          m4aUrl: item.m4a_url
        });
      });

      card.querySelector(".btn-del-hist").addEventListener("click", async () => {
        if (confirm("Delete this audio entry from library?")) {
          await fetch(`/api/history/${item.id}`, { method: "DELETE" });
          loadAudioLibrary();
        }
      });

      grid.appendChild(card);
    });
  } catch (err) {
    grid.innerHTML = `<div style="color: var(--danger);">Failed to load library: ${err.message}</div>`;
  }
}

const refreshHistBtn = document.getElementById("btn-refresh-history");
if (refreshHistBtn) {
  refreshHistBtn.addEventListener("click", loadAudioLibrary);
}

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
