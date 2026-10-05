// Quick Speech and Funny Presets Controller (Microsoft Neural Edition)

const FUNNY_PRESETS = {
  joke: {
    text: "Why do programmers prefer dark mode? Because light attracts bugs. And because coffee tastes 20% more dramatic in the shadows.",
    voice: "en-US-JennyNeural"
  },
  trailer: {
    text: "In a world where artificial intelligence controls the airwaves... one voice rose from the digital ether to speak the ultimate truth. Prepare your subwoofer.",
    voice: "en-US-ChristopherNeural"
  },
  pirate: {
    text: "Ahoy, ye salty barnacles and desktop scallywags! Grab yer finest tankards and hoist the black flag, for we sail at high tide into glorious audio conquest!",
    voice: "en-US-GuyNeural"
  },
  sarcastic: {
    text: "Oh fantastic, another sentence for me to read aloud verbatim while you sit there judging my cadence. Truly, I am living my best silicon existence.",
    voice: "en-GB-SoniaNeural"
  },
  radio: {
    text: "Flash! We interrupt this quiet afternoon with a special bulletin: Local authorities report an unprecedented surge in productivity, directly linked to high-speed AI voice generation!",
    voice: "en-US-EricNeural"
  },
  scifi: {
    text: "Vocal matrix synchronized. Harmonic frequencies locked. Welcome to the terminal, Commander. State your directive and prepare for acoustic transmission.",
    voice: "en-US-AriaNeural"
  },
  wizard: {
    text: "Hark, mortal traveler! You stand before the ancient forge of sound. Speak your words with reverence, lest the harmonic spirits awaken from their slumber!",
    voice: "en-GB-RyanNeural"
  }
};

const quickTextArea = document.getElementById("quick-text");
const charCountSpan = document.getElementById("char-count");
const quickVoiceSelect = document.getElementById("quick-voice-select");
const quickVoiceName = document.getElementById("quick-voice-name");
const quickVoiceDesc = document.getElementById("quick-voice-desc");
const quickFormatSelect = document.getElementById("quick-format");
const btnQuickGenerate = document.getElementById("btn-quick-generate");

// Update character counter
if (quickTextArea && charCountSpan) {
  quickTextArea.addEventListener("input", () => {
    const len = quickTextArea.value.length;
    charCountSpan.textContent = `${len} character${len === 1 ? "" : "s"}`;
  });
}

// Preset Chip Clicks
document.querySelectorAll(".chip-btn[data-preset]").forEach(btn => {
  btn.addEventListener("click", () => {
    const key = btn.dataset.preset;
    const preset = FUNNY_PRESETS[key];
    if (!preset) return;

    quickTextArea.value = preset.text;
    quickTextArea.dispatchEvent(new Event("input"));

    if (preset.voice && quickVoiceSelect) {
      quickVoiceSelect.value = preset.voice;
      quickVoiceSelect.dispatchEvent(new Event("change"));
    }
  });
});

// Update description card when voice changes
if (quickVoiceSelect) {
  quickVoiceSelect.addEventListener("change", () => {
    const selectedId = quickVoiceSelect.value;
    const v = cachedVoices.find(voice => voice.id === selectedId);
    if (v && quickVoiceName && quickVoiceDesc) {
      quickVoiceName.textContent = v.name;
      quickVoiceDesc.textContent = v.description || `${v.accent || "Standard"} tone for speech and narration.`;
    }
  });
}

// Populate Quick Voices Dropdown
window.populateQuickVoiceSelect = function(voices) {
  if (!quickVoiceSelect) return;
  quickVoiceSelect.innerHTML = "";
  
  voices.forEach(v => {
    const opt = document.createElement("option");
    opt.value = v.id;
    opt.textContent = `${v.name} (${v.gender || "Voice"})`;
    quickVoiceSelect.appendChild(opt);
  });

  const flagship = voices.find(v => v.is_flagship) || voices[0];
  if (flagship) {
    quickVoiceSelect.value = flagship.id;
  }

  // Trigger initial change
  quickVoiceSelect.dispatchEvent(new Event("change"));
};

// Generate Quick Speech
if (btnQuickGenerate) {
  btnQuickGenerate.addEventListener("click", async () => {
    const text = quickTextArea.value.trim();
    if (!text) {
      alert("Please enter some text to speak!");
      quickTextArea.focus();
      return;
    }

    const voiceId = quickVoiceSelect ? quickVoiceSelect.value : "en-US-ChristopherNeural";
    const format = quickFormatSelect ? quickFormatSelect.value : "mp3";

    btnQuickGenerate.disabled = true;
    const originalText = btnQuickGenerate.innerHTML;
    btnQuickGenerate.innerHTML = "⚡ Generating Speech...";

    try {
      const res = await fetch("/api/tts/quick", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: text,
          voice_id: voiceId,
          preferred_format: format
        })
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Server returned error ${res.status}`);
      }

      const data = await res.json();

      // Autoplay track in global audio player
      const voiceObj = cachedVoices.find(v => v.id === voiceId);
      const voiceLabel = voiceObj ? voiceObj.name : voiceId;

      const isGemini = voiceObj?.category === "gemini" || voiceObj?.provider === "gemini";
      const isKokoro = voiceObj?.category === "kokoro" || voiceObj?.provider === "openrouter";
      const engineLabel = isGemini ? "Google Gemini" : (isKokoro ? "Kokoro 82M" : "Microsoft Neural");

      window.playAudioTrack({
        url: data.audio_url,
        title: text.length > 50 ? text.substring(0, 50) + "..." : text,
        subtitle: `${voiceLabel} • ${engineLabel}`,
        mp3Url: data.mp3_url,
        m4aUrl: data.m4a_url
      });

    } catch (err) {
      alert("Speech generation failed: " + err.message);
    } finally {
      btnQuickGenerate.disabled = false;
      btnQuickGenerate.innerHTML = originalText;
    }
  });
}
