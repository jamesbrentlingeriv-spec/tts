import json
import uuid
import time
from typing import List, Dict, Any, Optional
from app.config import VOICES_FILE, HISTORY_FILE, load_config

# 1. Curated High-Fidelity Microsoft Neural Voices (Fast, Free, Studio Quality)
NEURAL_VOICES = [
    # Flagship Narrators
    {
        "id": "en-US-ChristopherNeural",
        "name": "Christopher (Flagship)",
        "gender": "Male",
        "base_voice": "en-US-ChristopherNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "en-US",
        "language_name": "English (US)",
        "accent": "American",
        "is_custom": False,
        "is_flagship": True,
        "description": "Deep, authoritative, cinematic baritone. Gold-standard for audiobooks, dramatic reading, and deep voiceovers.",
        "tags": ["Flagship", "Deep Baritone", "Cinematic", "Audiobook", "Male"]
    },
    {
        "id": "en-US-JennyNeural",
        "name": "Jenny (Flagship)",
        "gender": "Female",
        "base_voice": "en-US-JennyNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "en-US",
        "language_name": "English (US)",
        "accent": "American",
        "is_custom": False,
        "is_flagship": True,
        "description": "Warm, exquisitely natural, fluid flagship narrator. Perfect for audiobooks, articles, and long-form storytelling.",
        "tags": ["Flagship", "Warm", "Natural", "Audiobook", "Female"]
    },
    # American English - Male
    {
        "id": "en-US-GuyNeural",
        "name": "Guy",
        "gender": "Male",
        "base_voice": "en-US-GuyNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "en-US",
        "language_name": "English (US)",
        "accent": "American",
        "is_custom": False,
        "description": "Relaxed, natural, broadcast-grade conversational tone. Ideal for podcasts, modern narration, and explainer content.",
        "tags": ["Conversational", "Podcast", "Friendly", "Broadcast", "Male"]
    },
    {
        "id": "en-US-AndrewNeural",
        "name": "Andrew",
        "gender": "Male",
        "base_voice": "en-US-AndrewNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "en-US",
        "language_name": "English (US)",
        "accent": "American",
        "is_custom": False,
        "description": "Crisp, confident, articulate modern delivery. Great for business, tutorials, and clear reading.",
        "tags": ["Confident", "Articulate", "Modern", "Male"]
    },
    {
        "id": "en-US-EricNeural",
        "name": "Eric",
        "gender": "Male",
        "base_voice": "en-US-EricNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "en-US",
        "language_name": "English (US)",
        "accent": "American",
        "is_custom": False,
        "description": "Grounded, smooth, and resonant masculine voice with great presence.",
        "tags": ["Grounded", "Resonant", "Narrator", "Male"]
    },
    {
        "id": "en-US-BrianNeural",
        "name": "Brian",
        "gender": "Male",
        "base_voice": "en-US-BrianNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "en-US",
        "language_name": "English (US)",
        "accent": "American",
        "is_custom": False,
        "description": "Deep, sophisticated, executive clarity. Well-suited for formal and technical reading.",
        "tags": ["Sophisticated", "Deep", "Professional", "Male"]
    },
    {
        "id": "en-US-RogerNeural",
        "name": "Roger",
        "gender": "Male",
        "base_voice": "en-US-RogerNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "en-US",
        "language_name": "English (US)",
        "accent": "American",
        "is_custom": False,
        "description": "Mature, calm, measured, and reassuring male voice.",
        "tags": ["Mature", "Calm", "Narrator", "Male"]
    },
    {
        "id": "en-US-SteffanNeural",
        "name": "Steffan",
        "gender": "Male",
        "base_voice": "en-US-SteffanNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "en-US",
        "language_name": "English (US)",
        "accent": "American",
        "is_custom": False,
        "description": "Warm, expressive storytelling delivery with dramatic range.",
        "tags": ["Expressive", "Warm", "Storytelling", "Male"]
    },
    # American English - Female
    {
        "id": "en-US-AriaNeural",
        "name": "Aria",
        "gender": "Female",
        "base_voice": "en-US-AriaNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "en-US",
        "language_name": "English (US)",
        "accent": "American",
        "is_custom": False,
        "description": "Dynamic, expressive, and conversational. Rich emotional inflection.",
        "tags": ["Expressive", "Dynamic", "Conversational", "Female"]
    },
    {
        "id": "en-US-AvaNeural",
        "name": "Ava",
        "gender": "Female",
        "base_voice": "en-US-AvaNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "en-US",
        "language_name": "English (US)",
        "accent": "American",
        "is_custom": False,
        "description": "Soft, gentle, intimate storytelling voice. Excellent for poetry and soothing audiobooks.",
        "tags": ["Gentle", "Soft", "Intimate", "Female"]
    },
    {
        "id": "en-US-EmmaNeural",
        "name": "Emma",
        "gender": "Female",
        "base_voice": "en-US-EmmaNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "en-US",
        "language_name": "English (US)",
        "accent": "American",
        "is_custom": False,
        "description": "Crisp, bright, and cheerful modern tone. Friendly and approachable.",
        "tags": ["Bright", "Crisp", "Upbeat", "Female"]
    },
    {
        "id": "en-US-AnaNeural",
        "name": "Ana",
        "gender": "Female",
        "base_voice": "en-US-AnaNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "en-US",
        "language_name": "English (US)",
        "accent": "American",
        "is_custom": False,
        "description": "Youthful, energetic, friendly delivery.",
        "tags": ["Youthful", "Energetic", "Friendly", "Female"]
    },
    {
        "id": "en-US-MichelleNeural",
        "name": "Michelle",
        "gender": "Female",
        "base_voice": "en-US-MichelleNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "en-US",
        "language_name": "English (US)",
        "accent": "American",
        "is_custom": False,
        "description": "Professional, composed, clear broadcast-quality female delivery.",
        "tags": ["Professional", "Composed", "Broadcast", "Female"]
    },
    # British English (en-GB)
    {
        "id": "en-GB-RyanNeural",
        "name": "Ryan (British)",
        "gender": "Male",
        "base_voice": "en-GB-RyanNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "en-GB",
        "language_name": "English (UK)",
        "accent": "British",
        "is_custom": False,
        "description": "Smooth, refined British male narrator. Great for fantasy novels, documentaries, and history.",
        "tags": ["British", "Smooth", "Refined", "Documentary", "Male"]
    },
    {
        "id": "en-GB-ThomasNeural",
        "name": "Thomas (British)",
        "gender": "Male",
        "base_voice": "en-GB-ThomasNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "en-GB",
        "language_name": "English (UK)",
        "accent": "British",
        "is_custom": False,
        "description": "Distinguished, warm British male voice with natural resonance.",
        "tags": ["British", "Distinguished", "Warm", "Male"]
    },
    {
        "id": "en-GB-SoniaNeural",
        "name": "Sonia (British)",
        "gender": "Female",
        "base_voice": "en-GB-SoniaNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "en-GB",
        "language_name": "English (UK)",
        "accent": "British",
        "is_custom": False,
        "description": "Elegant, aristocratic British female voice. Smooth, poetic, and pristine.",
        "tags": ["British", "Elegant", "Pristine", "Female"]
    },
    {
        "id": "en-GB-LibbyNeural",
        "name": "Libby (British)",
        "gender": "Female",
        "base_voice": "en-GB-LibbyNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "en-GB",
        "language_name": "English (UK)",
        "accent": "British",
        "is_custom": False,
        "description": "Friendly, charming British tone with natural conversational warmth.",
        "tags": ["British", "Charming", "Warm", "Female"]
    },
    # Australian & Canadian English
    {
        "id": "en-AU-WilliamMultilingualNeural",
        "name": "William (Australian)",
        "gender": "Male",
        "base_voice": "en-AU-WilliamMultilingualNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "en-AU",
        "language_name": "English (AU)",
        "accent": "Australian",
        "is_custom": False,
        "description": "Deep, calm Australian male narrator.",
        "tags": ["Australian", "Deep", "Calm", "Male"]
    },
    {
        "id": "en-AU-NatashaNeural",
        "name": "Natasha (Australian)",
        "gender": "Female",
        "base_voice": "en-AU-NatashaNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "en-AU",
        "language_name": "English (AU)",
        "accent": "Australian",
        "is_custom": False,
        "description": "Warm, natural Australian female delivery.",
        "tags": ["Australian", "Warm", "Natural", "Female"]
    },
    {
        "id": "en-CA-LiamNeural",
        "name": "Liam (Canadian)",
        "gender": "Male",
        "base_voice": "en-CA-LiamNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "en-CA",
        "language_name": "English (CA)",
        "accent": "Canadian",
        "is_custom": False,
        "description": "Modern, articulate Canadian male voice.",
        "tags": ["Canadian", "Modern", "Articulate", "Male"]
    },
    {
        "id": "en-CA-ClaraNeural",
        "name": "Clara (Canadian)",
        "gender": "Female",
        "base_voice": "en-CA-ClaraNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "en-CA",
        "language_name": "English (CA)",
        "accent": "Canadian",
        "is_custom": False,
        "description": "Clean, balanced Canadian female narrator.",
        "tags": ["Canadian", "Clean", "Balanced", "Female"]
    },
    {
        "id": "en-IN-PrabhatNeural",
        "name": "Prabhat (Indian)",
        "gender": "Male",
        "base_voice": "en-IN-PrabhatNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "en-IN",
        "language_name": "English (India)",
        "accent": "Indian",
        "is_custom": False,
        "description": "Articulate, pleasant Indian English male narrator.",
        "tags": ["Indian", "Articulate", "Pleasant", "Male"]
    },
    {
        "id": "en-IN-NeerjaExpressiveNeural",
        "name": "Neerja (Indian)",
        "gender": "Female",
        "base_voice": "en-IN-NeerjaExpressiveNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "en-IN",
        "language_name": "English (India)",
        "accent": "Indian",
        "is_custom": False,
        "description": "Expressive, melodic Indian English female narrator.",
        "tags": ["Indian", "Expressive", "Melodic", "Female"]
    },
    # International Voices
    {
        "id": "es-ES-AlvaroNeural",
        "name": "Alvaro (Spanish)",
        "gender": "Male",
        "base_voice": "es-ES-AlvaroNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "es-ES",
        "language_name": "Spanish (Spain)",
        "accent": "Castilian",
        "is_custom": False,
        "description": "Warm, confident Spanish male voice.",
        "tags": ["Spanish", "Warm", "Male"]
    },
    {
        "id": "es-ES-ElviraNeural",
        "name": "Elvira (Spanish)",
        "gender": "Female",
        "base_voice": "es-ES-ElviraNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "es-ES",
        "language_name": "Spanish (Spain)",
        "accent": "Castilian",
        "is_custom": False,
        "description": "Clear, expressive Spanish female narrator.",
        "tags": ["Spanish", "Expressive", "Female"]
    },
    {
        "id": "fr-FR-HenriNeural",
        "name": "Henri (French)",
        "gender": "Male",
        "base_voice": "fr-FR-HenriNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "fr-FR",
        "language_name": "French (France)",
        "accent": "French",
        "is_custom": False,
        "description": "Smooth, refined French male narrator.",
        "tags": ["French", "Smooth", "Male"]
    },
    {
        "id": "fr-FR-DeniseNeural",
        "name": "Denise (French)",
        "gender": "Female",
        "base_voice": "fr-FR-DeniseNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "fr-FR",
        "language_name": "French (France)",
        "accent": "French",
        "is_custom": False,
        "description": "Elegant, natural French female voice.",
        "tags": ["French", "Elegant", "Female"]
    },
    {
        "id": "de-DE-ConradNeural",
        "name": "Conrad (German)",
        "gender": "Male",
        "base_voice": "de-DE-ConradNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "de-DE",
        "language_name": "German (Germany)",
        "accent": "German",
        "is_custom": False,
        "description": "Deep, authoritative German male voice.",
        "tags": ["German", "Deep", "Male"]
    },
    {
        "id": "de-DE-KatjaNeural",
        "name": "Katja (German)",
        "gender": "Female",
        "base_voice": "de-DE-KatjaNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "de-DE",
        "language_name": "German (Germany)",
        "accent": "German",
        "is_custom": False,
        "description": "Clear, pleasant German female narrator.",
        "tags": ["German", "Clear", "Female"]
    },
    {
        "id": "ja-JP-KeitaNeural",
        "name": "Keita (Japanese)",
        "gender": "Male",
        "base_voice": "ja-JP-KeitaNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "ja-JP",
        "language_name": "Japanese",
        "accent": "Tokyo",
        "is_custom": False,
        "description": "Deep, calm Japanese male voice.",
        "tags": ["Japanese", "Calm", "Male"]
    },
    {
        "id": "ja-JP-NanamiNeural",
        "name": "Nanami (Japanese)",
        "gender": "Female",
        "base_voice": "ja-JP-NanamiNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "ja-JP",
        "language_name": "Japanese",
        "accent": "Tokyo",
        "is_custom": False,
        "description": "Bright, clear Japanese female voice.",
        "tags": ["Japanese", "Bright", "Female"]
    },
    {
        "id": "zh-CN-YunxiNeural",
        "name": "Yunxi (Mandarin)",
        "gender": "Male",
        "base_voice": "zh-CN-YunxiNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "zh-CN",
        "language_name": "Chinese (Mandarin)",
        "accent": "Mainland",
        "is_custom": False,
        "description": "Rich, resonant Mandarin male voice.",
        "tags": ["Mandarin", "Resonant", "Male"]
    },
    {
        "id": "zh-CN-XiaoxiaoNeural",
        "name": "Xiaoxiao (Mandarin)",
        "gender": "Female",
        "base_voice": "zh-CN-XiaoxiaoNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "zh-CN",
        "language_name": "Chinese (Mandarin)",
        "accent": "Mainland",
        "is_custom": False,
        "description": "Gentle, expressive Mandarin female voice.",
        "tags": ["Mandarin", "Gentle", "Female"]
    },
    {
        "id": "it-IT-DiegoNeural",
        "name": "Diego (Italian)",
        "gender": "Male",
        "base_voice": "it-IT-DiegoNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "it-IT",
        "language_name": "Italian (Italy)",
        "accent": "Italian",
        "is_custom": False,
        "description": "Warm, melodious Italian male voice.",
        "tags": ["Italian", "Warm", "Male"]
    },
    {
        "id": "it-IT-ElsaNeural",
        "name": "Elsa (Italian)",
        "gender": "Female",
        "base_voice": "it-IT-ElsaNeural",
        "category": "neural",
        "provider": "microsoft",
        "language": "it-IT",
        "language_name": "Italian (Italy)",
        "accent": "Italian",
        "is_custom": False,
        "description": "Expressive, clear Italian female narrator.",
        "tags": ["Italian", "Expressive", "Female"]
    }
]

# 2. All 54 Official Kokoro-82M Voices (OpenRouter)
KOKORO_VOICES = [
    # American English - Female (11)
    {"id": "af_heart", "name": "Heart (Flagship)", "gender": "Female", "base_voice": "af_heart", "category": "kokoro", "provider": "openrouter", "language": "en-US", "language_name": "English (US)", "accent": "American", "is_custom": False, "is_flagship": True, "description": "Grade A flagship voice. Warm, exquisitely natural, and expressive.", "tags": ["Grade A", "Flagship", "Warm", "Expressive"]},
    {"id": "af_bella", "name": "Bella", "gender": "Female", "base_voice": "af_bella", "category": "kokoro", "provider": "openrouter", "language": "en-US", "language_name": "English (US)", "accent": "American", "is_custom": False, "description": "Grade A- articulate, dynamic, and clear American female delivery.", "tags": ["Grade A-", "Clear", "Articulate"]},
    {"id": "af_nicole", "name": "Nicole", "gender": "Female", "base_voice": "af_nicole", "category": "kokoro", "provider": "openrouter", "language": "en-US", "language_name": "English (US)", "accent": "American", "is_custom": False, "description": "Grade B- smooth, conversational, headphone-quality podcast tone.", "tags": ["Grade B-", "Conversational", "Smooth"]},
    {"id": "af_aoede", "name": "Aoede", "gender": "Female", "base_voice": "af_aoede", "category": "kokoro", "provider": "openrouter", "language": "en-US", "language_name": "English (US)", "accent": "American", "is_custom": False, "description": "Grade B+ melodic, classical, and storytelling tone.", "tags": ["Grade B+", "Melodic", "Classical"]},
    {"id": "af_kore", "name": "Kore", "gender": "Female", "base_voice": "af_kore", "category": "kokoro", "provider": "openrouter", "language": "en-US", "language_name": "English (US)", "accent": "American", "is_custom": False, "description": "Grade B- crisp, modern, and energetic female delivery.", "tags": ["Grade B-", "Crisp", "Energetic"]},
    {"id": "af_sarah", "name": "Sarah", "gender": "Female", "base_voice": "af_sarah", "category": "kokoro", "provider": "openrouter", "language": "en-US", "language_name": "English (US)", "accent": "American", "is_custom": False, "description": "Grade B- balanced, neutral American tone.", "tags": ["Grade B-", "Balanced", "Neutral"]},
    {"id": "af_nova", "name": "Nova", "gender": "Female", "base_voice": "af_nova", "category": "kokoro", "provider": "openrouter", "language": "en-US", "language_name": "English (US)", "accent": "American", "is_custom": False, "description": "Grade B- bright, cheerful, modern commercial voice.", "tags": ["Grade B-", "Bright", "Commercial"]},
    {"id": "af_sky", "name": "Sky", "gender": "Female", "base_voice": "af_sky", "category": "kokoro", "provider": "openrouter", "language": "en-US", "language_name": "English (US)", "accent": "American", "is_custom": False, "description": "Grade B- breezy, youthful, and upbeat female tone.", "tags": ["Grade B-", "Youthful", "Upbeat"]},
    {"id": "af_alloy", "name": "Alloy", "gender": "Female", "base_voice": "af_alloy", "category": "kokoro", "provider": "openrouter", "language": "en-US", "language_name": "English (US)", "accent": "American", "is_custom": False, "description": "Grade B neutral, direct, assistant-style tone.", "tags": ["Grade B", "Assistant", "Direct"]},
    {"id": "af_jessica", "name": "Jessica", "gender": "Female", "base_voice": "af_jessica", "category": "kokoro", "provider": "openrouter", "language": "en-US", "language_name": "English (US)", "accent": "American", "is_custom": False, "description": "Grade B expressive, friendly conversationalist.", "tags": ["Grade B", "Friendly"]},
    {"id": "af_river", "name": "River", "gender": "Female", "base_voice": "af_river", "category": "kokoro", "provider": "openrouter", "language": "en-US", "language_name": "English (US)", "accent": "American", "is_custom": False, "description": "Grade B calm, meditative, and smooth female voice.", "tags": ["Grade B", "Calm", "Meditative"]},

    # American English - Male (9)
    {"id": "am_michael", "name": "Michael (Flagship)", "gender": "Male", "base_voice": "am_michael", "category": "kokoro", "provider": "openrouter", "language": "en-US", "language_name": "English (US)", "accent": "American", "is_custom": False, "is_flagship": True, "description": "Grade A- flagship American male voice. Confident, warm, and natural.", "tags": ["Grade A-", "Flagship", "Confident", "Warm"]},
    {"id": "am_adam", "name": "Adam", "gender": "Male", "base_voice": "am_adam", "category": "kokoro", "provider": "openrouter", "language": "en-US", "language_name": "English (US)", "accent": "American", "is_custom": False, "description": "Grade B- deep, direct, and authoritative American delivery.", "tags": ["Grade B-", "Deep", "Authoritative"]},
    {"id": "am_echo", "name": "Echo", "gender": "Male", "base_voice": "am_echo", "category": "kokoro", "provider": "openrouter", "language": "en-US", "language_name": "English (US)", "accent": "American", "is_custom": False, "description": "Grade C+ smooth, modern, podcast-style male voice.", "tags": ["Grade C+", "Podcast"]},
    {"id": "am_eric", "name": "Eric", "gender": "Male", "base_voice": "am_eric", "category": "kokoro", "provider": "openrouter", "language": "en-US", "language_name": "English (US)", "accent": "American", "is_custom": False, "description": "Grade C+ relaxed, casual American narrator.", "tags": ["Grade C+", "Casual"]},
    {"id": "am_fenrir", "name": "Fenrir", "gender": "Male", "base_voice": "am_fenrir", "category": "kokoro", "provider": "openrouter", "language": "en-US", "language_name": "English (US)", "accent": "American", "is_custom": False, "description": "Grade B+ dramatic, intense, cinematic baritone.", "tags": ["Grade B+", "Cinematic", "Dramatic", "Trailer"]},
    {"id": "am_liam", "name": "Liam", "gender": "Male", "base_voice": "am_liam", "category": "kokoro", "provider": "openrouter", "language": "en-US", "language_name": "English (US)", "accent": "American", "is_custom": False, "description": "Grade C modern, youthful American male voice.", "tags": ["Grade C", "Youthful"]},
    {"id": "am_onyx", "name": "Onyx", "gender": "Male", "base_voice": "am_onyx", "category": "kokoro", "provider": "openrouter", "language": "en-US", "language_name": "English (US)", "accent": "American", "is_custom": False, "description": "Grade B deep, gravelly, commanding voice.", "tags": ["Grade B", "Deep", "Commanding"]},
    {"id": "am_puck", "name": "Puck", "gender": "Male", "base_voice": "am_puck", "category": "kokoro", "provider": "openrouter", "language": "en-US", "language_name": "English (US)", "accent": "American", "is_custom": False, "description": "Grade B playful, theatrical, expressive character voice.", "tags": ["Grade B", "Theatrical", "Character"]},
    {"id": "am_santa", "name": "Santa", "gender": "Male", "base_voice": "am_santa", "category": "kokoro", "provider": "openrouter", "language": "en-US", "language_name": "English (US)", "accent": "American", "is_custom": False, "description": "Grade C jovial, hearty, deep festive male delivery.", "tags": ["Grade C", "Jovial", "Warm"]},

    # British English - Female (4)
    {"id": "bf_emma", "name": "Emma (British)", "gender": "Female", "base_voice": "bf_emma", "category": "kokoro", "provider": "openrouter", "language": "en-GB", "language_name": "English (UK)", "accent": "British", "is_custom": False, "is_flagship": True, "description": "Grade A- flagship British female. Refined, eloquent, and natural.", "tags": ["Grade A-", "Flagship", "British", "Eloquent"]},
    {"id": "bf_isabella", "name": "Isabella (British)", "gender": "Female", "base_voice": "bf_isabella", "category": "kokoro", "provider": "openrouter", "language": "en-GB", "language_name": "English (UK)", "accent": "British", "is_custom": False, "description": "Grade B elegant, aristocratic British delivery.", "tags": ["Grade B", "British", "Elegant"]},
    {"id": "bf_alice", "name": "Alice (British)", "gender": "Female", "base_voice": "bf_alice", "category": "kokoro", "provider": "openrouter", "language": "en-GB", "language_name": "English (UK)", "accent": "British", "is_custom": False, "description": "Grade B- crisp, pleasant British narrator.", "tags": ["Grade B-", "British", "Crisp"]},
    {"id": "bf_lily", "name": "Lily (British)", "gender": "Female", "base_voice": "bf_lily", "category": "kokoro", "provider": "openrouter", "language": "en-GB", "language_name": "English (UK)", "accent": "British", "is_custom": False, "description": "Grade B- gentle, melodic British tone.", "tags": ["Grade B-", "British", "Gentle"]},

    # British English - Male (4)
    {"id": "bm_george", "name": "George (British)", "gender": "Male", "base_voice": "bm_george", "category": "kokoro", "provider": "openrouter", "language": "en-GB", "language_name": "English (UK)", "accent": "British", "is_custom": False, "is_flagship": True, "description": "Grade B flagship British male. Deep, distinguished, classic BBC broadcaster.", "tags": ["Grade B", "Flagship", "British", "Distinguished"]},
    {"id": "bm_fable", "name": "Fable (British)", "gender": "Male", "base_voice": "bm_fable", "category": "kokoro", "provider": "openrouter", "language": "en-GB", "language_name": "English (UK)", "accent": "British", "is_custom": False, "description": "Grade B warm, whimsical, fantasy storyteller tone.", "tags": ["Grade B", "British", "Storyteller"]},
    {"id": "bm_lewis", "name": "Lewis (British)", "gender": "Male", "base_voice": "bm_lewis", "category": "kokoro", "provider": "openrouter", "language": "en-GB", "language_name": "English (UK)", "accent": "British", "is_custom": False, "description": "Grade C+ crisp, intellectual British narrator.", "tags": ["Grade C+", "British", "Intellectual"]},
    {"id": "bm_daniel", "name": "Daniel (British)", "gender": "Male", "base_voice": "bm_daniel", "category": "kokoro", "provider": "openrouter", "language": "en-GB", "language_name": "English (UK)", "accent": "British", "is_custom": False, "description": "Grade C measured, formal British male delivery.", "tags": ["Grade C", "British"]},

    # Japanese (5)
    {"id": "jf_alpha", "name": "Alpha (Japanese)", "gender": "Female", "base_voice": "jf_alpha", "category": "kokoro", "provider": "openrouter", "language": "ja-JP", "language_name": "Japanese", "accent": "Japanese", "is_custom": False, "description": "Grade A- natural, expressive Japanese female.", "tags": ["Grade A-", "Japanese", "Anime"]},
    {"id": "jf_gongitsune", "name": "Gongitsune (Japanese)", "gender": "Female", "base_voice": "jf_gongitsune", "category": "kokoro", "provider": "openrouter", "language": "ja-JP", "language_name": "Japanese", "accent": "Japanese", "is_custom": False, "description": "Grade B traditional Japanese storytelling tone.", "tags": ["Grade B", "Japanese"]},
    {"id": "jf_nezumi", "name": "Nezumi (Japanese)", "gender": "Female", "base_voice": "jf_nezumi", "category": "kokoro", "provider": "openrouter", "language": "ja-JP", "language_name": "Japanese", "accent": "Japanese", "is_custom": False, "description": "Grade B- bright, energetic Japanese character voice.", "tags": ["Grade B-", "Japanese"]},
    {"id": "jf_tebukuro", "name": "Tebukuro (Japanese)", "gender": "Female", "base_voice": "jf_tebukuro", "category": "kokoro", "provider": "openrouter", "language": "ja-JP", "language_name": "Japanese", "accent": "Japanese", "is_custom": False, "description": "Grade C gentle, soothing Japanese delivery.", "tags": ["Grade C", "Japanese"]},
    {"id": "jm_kumo", "name": "Kumo (Japanese)", "gender": "Male", "base_voice": "jm_kumo", "category": "kokoro", "provider": "openrouter", "language": "ja-JP", "language_name": "Japanese", "accent": "Japanese", "is_custom": False, "description": "Grade B deep, calm Japanese male narrator.", "tags": ["Grade B", "Japanese", "Deep"]},

    # Mandarin Chinese (8)
    {"id": "zf_xiaobei", "name": "Xiaobei (Mandarin)", "gender": "Female", "base_voice": "zf_xiaobei", "category": "kokoro", "provider": "openrouter", "language": "zh-CN", "language_name": "Mandarin Chinese", "accent": "Mainland", "is_custom": False, "description": "Grade B lively, northern Beijing-accented female.", "tags": ["Grade B", "Mandarin"]},
    {"id": "zf_xiaoni", "name": "Xiaoni (Mandarin)", "gender": "Female", "base_voice": "zf_xiaoni", "category": "kokoro", "provider": "openrouter", "language": "zh-CN", "language_name": "Mandarin Chinese", "accent": "Mainland", "is_custom": False, "description": "Grade B clear, professional broadcast Mandarin.", "tags": ["Grade B", "Mandarin", "Broadcast"]},
    {"id": "zf_xiaoxiao", "name": "Xiaoxiao (Mandarin)", "gender": "Female", "base_voice": "zf_xiaoxiao", "category": "kokoro", "provider": "openrouter", "language": "zh-CN", "language_name": "Mandarin Chinese", "accent": "Mainland", "is_custom": False, "description": "Grade B- gentle, expressive audiobook narrator.", "tags": ["Grade B-", "Mandarin"]},
    {"id": "zf_xiaoyi", "name": "Xiaoyi (Mandarin)", "gender": "Female", "base_voice": "zf_xiaoyi", "category": "kokoro", "provider": "openrouter", "language": "zh-CN", "language_name": "Mandarin Chinese", "accent": "Mainland", "is_custom": False, "description": "Grade C natural conversational Mandarin tone.", "tags": ["Grade C", "Mandarin"]},
    {"id": "zm_yunjian", "name": "Yunjian (Mandarin)", "gender": "Male", "base_voice": "zm_yunjian", "category": "kokoro", "provider": "openrouter", "language": "zh-CN", "language_name": "Mandarin Chinese", "accent": "Mainland", "is_custom": False, "description": "Grade B deep, cinematic Mandarin documentary voice.", "tags": ["Grade B", "Mandarin", "Documentary"]},
    {"id": "zm_yunxi", "name": "Yunxi (Mandarin)", "gender": "Male", "base_voice": "zm_yunxi", "category": "kokoro", "provider": "openrouter", "language": "zh-CN", "language_name": "Mandarin Chinese", "accent": "Mainland", "is_custom": False, "description": "Grade B- warm, modern male delivery.", "tags": ["Grade B-", "Mandarin"]},
    {"id": "zm_yunxia", "name": "Yunxia (Mandarin)", "gender": "Male", "base_voice": "zm_yunxia", "category": "kokoro", "provider": "openrouter", "language": "zh-CN", "language_name": "Mandarin Chinese", "accent": "Mainland", "is_custom": False, "description": "Grade C youthful, energetic storytelling tone.", "tags": ["Grade C", "Mandarin"]},
    {"id": "zm_yunyang", "name": "Yunyang (Mandarin)", "gender": "Male", "base_voice": "zm_yunyang", "category": "kokoro", "provider": "openrouter", "language": "zh-CN", "language_name": "Mandarin Chinese", "accent": "Mainland", "is_custom": False, "description": "Grade C balanced, clear explanatory delivery.", "tags": ["Grade C", "Mandarin"]},

    # Spanish (3)
    {"id": "ef_dora", "name": "Dora (Spanish)", "gender": "Female", "base_voice": "ef_dora", "category": "kokoro", "provider": "openrouter", "language": "es-ES", "language_name": "Spanish", "accent": "Castilian", "is_custom": False, "description": "Grade B natural, clear Castilian Spanish delivery.", "tags": ["Grade B", "Spanish"]},
    {"id": "em_alex", "name": "Alex (Spanish)", "gender": "Male", "base_voice": "em_alex", "category": "kokoro", "provider": "openrouter", "language": "es-ES", "language_name": "Spanish", "accent": "Castilian", "is_custom": False, "description": "Grade B confident, warm Spanish male delivery.", "tags": ["Grade B", "Spanish", "Warm"]},
    {"id": "em_santa", "name": "Santa (Spanish)", "gender": "Male", "base_voice": "em_santa", "category": "kokoro", "provider": "openrouter", "language": "es-ES", "language_name": "Spanish", "accent": "Castilian", "is_custom": False, "description": "Grade C hearty, expressive festive Spanish voice.", "tags": ["Grade C", "Spanish"]},

    # French, Hindi, Italian (5)
    {"id": "ff_siwis", "name": "Siwis (French)", "gender": "Female", "base_voice": "ff_siwis", "category": "kokoro", "provider": "openrouter", "language": "fr-FR", "language_name": "French", "accent": "French", "is_custom": False, "description": "Grade B- smooth, elegant Parisian French female delivery.", "tags": ["Grade B-", "French", "Elegant"]},
    {"id": "hf_alpha", "name": "Alpha (Hindi)", "gender": "Female", "base_voice": "hf_alpha", "category": "kokoro", "provider": "openrouter", "language": "hi-IN", "language_name": "Hindi", "accent": "Indian", "is_custom": False, "description": "Grade B- natural, expressive Hindi female.", "tags": ["Grade B-", "Hindi"]},
    {"id": "hf_beta", "name": "Beta (Hindi)", "gender": "Female", "base_voice": "hf_beta", "category": "kokoro", "provider": "openrouter", "language": "hi-IN", "language_name": "Hindi", "accent": "Indian", "is_custom": False, "description": "Grade C clear, gentle Hindi female voice.", "tags": ["Grade C", "Hindi"]},
    {"id": "hm_omega", "name": "Omega (Hindi)", "gender": "Male", "base_voice": "hm_omega", "category": "kokoro", "provider": "openrouter", "language": "hi-IN", "language_name": "Hindi", "accent": "Indian", "is_custom": False, "description": "Grade B- deep, resonant Hindi male voice.", "tags": ["Grade B-", "Hindi", "Deep"]},
    {"id": "hm_psi", "name": "Psi (Hindi)", "gender": "Male", "base_voice": "hm_psi", "category": "kokoro", "provider": "openrouter", "language": "hi-IN", "language_name": "Hindi", "accent": "Indian", "is_custom": False, "description": "Grade C calm, steady Hindi narrator.", "tags": ["Grade C", "Hindi"]}
]

# 3. Google Gemini 2.0 Native Audio Voices (Highly Expressive, Adaptive, Studio Style)
GEMINI_VOICES = [
    {
        "id": "Puck",
        "name": "Puck (Flagship)",
        "gender": "Male",
        "base_voice": "Puck",
        "category": "gemini",
        "provider": "gemini",
        "language": "en-US",
        "language_name": "English (US)",
        "accent": "American",
        "is_custom": False,
        "is_flagship": True,
        "description": "Playful, energetic, engaging modern male voice with nuanced dynamic range.",
        "tags": ["Flagship", "Playful", "Conversational", "Audiobook", "Male"]
    },
    {
        "id": "Charon",
        "name": "Charon (Flagship)",
        "gender": "Male",
        "base_voice": "Charon",
        "category": "gemini",
        "provider": "gemini",
        "language": "en-US",
        "language_name": "English (US)",
        "accent": "American",
        "is_custom": False,
        "is_flagship": True,
        "description": "Deep, resonant, authoritative cinematic baritone. Superb for intense narration.",
        "tags": ["Flagship", "Deep", "Cinematic", "Resonant", "Male"]
    },
    {
        "id": "Kore",
        "name": "Kore",
        "gender": "Female",
        "base_voice": "Kore",
        "category": "gemini",
        "provider": "gemini",
        "language": "en-US",
        "language_name": "English (US)",
        "accent": "American",
        "is_custom": False,
        "is_flagship": True,
        "description": "Calm, gentle, soothing feminine narrator for poetry and intimate reading.",
        "tags": ["Soothing", "Calm", "Gentle", "Female"]
    },
    {
        "id": "Fenrir",
        "name": "Fenrir",
        "gender": "Male",
        "base_voice": "Fenrir",
        "category": "gemini",
        "provider": "gemini",
        "language": "en-US",
        "language_name": "English (US)",
        "accent": "American",
        "is_custom": False,
        "description": "Bold, dramatic, commanding delivery for action and epic fantasy.",
        "tags": ["Bold", "Dramatic", "Commanding", "Male"]
    },
    {
        "id": "Aoede",
        "name": "Aoede",
        "gender": "Female",
        "base_voice": "Aoede",
        "category": "gemini",
        "provider": "gemini",
        "language": "en-US",
        "language_name": "English (US)",
        "accent": "American",
        "is_custom": False,
        "description": "Melodic, expressive, theatrical delivery with artistic cadence.",
        "tags": ["Melodic", "Expressive", "Theatrical", "Female"]
    }
]

def load_voices(engine: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Loads voices filtered by engine:
    - 'gemini': returns Google Gemini voices
    - 'microsoft_neural': returns Microsoft Neural voices
    - 'kokoro' or 'openrouter': returns Kokoro-82M voices
    - 'all': returns all voices across all engines
    - None: uses currently active engine from config
    """
    if not engine:
        cfg = load_config()
        engine = cfg.get("engine", "gemini")

    custom_voices = []
    if VOICES_FILE.exists():
        try:
            with open(VOICES_FILE, "r", encoding="utf-8") as f:
                custom_voices = json.load(f)
        except Exception:
            pass

    if engine == "all":
        base_list = list(GEMINI_VOICES) + list(KOKORO_VOICES) + list(NEURAL_VOICES)
    elif engine == "gemini":
        base_list = list(GEMINI_VOICES)
    elif engine in ("kokoro", "openrouter"):
        base_list = list(KOKORO_VOICES)
    else:
        base_list = list(NEURAL_VOICES)

    return base_list + custom_voices

def save_custom_voice(voice_data: Dict[str, Any]) -> Dict[str, Any]:
    """Saves a user-customized voice or bookmark."""
    custom_voices = []
    if VOICES_FILE.exists():
        try:
            with open(VOICES_FILE, "r", encoding="utf-8") as f:
                custom_voices = json.load(f)
        except Exception:
            pass

    if "id" not in voice_data:
        voice_data["id"] = f"custom_{uuid.uuid4().hex[:8]}"
    voice_data["is_custom"] = True
    voice_data["category"] = "custom"

    # Replace existing if updating
    custom_voices = [v for v in custom_voices if v.get("id") != voice_data["id"]]
    custom_voices.append(voice_data)

    with open(VOICES_FILE, "w", encoding="utf-8") as f:
        json.dump(custom_voices, f, indent=2)

    return voice_data

def delete_custom_voice(voice_id: str) -> bool:
    """Deletes a custom voice by ID."""
    if not VOICES_FILE.exists():
        return False
    try:
        with open(VOICES_FILE, "r", encoding="utf-8") as f:
            custom_voices = json.load(f)
        filtered = [v for v in custom_voices if v.get("id") != voice_id]
        if len(filtered) != len(custom_voices):
            with open(VOICES_FILE, "w", encoding="utf-8") as f:
                json.dump(filtered, f, indent=2)
            return True
    except Exception:
        pass
    return False

def get_voice_by_id(voice_id: str) -> Optional[Dict[str, Any]]:
    if not voice_id:
        return GEMINI_VOICES[0]
    all_voices = list(GEMINI_VOICES) + list(KOKORO_VOICES) + list(NEURAL_VOICES)
    vid_lower = voice_id.lower().strip()
    for v in all_voices:
        if (
            v.get("id", "").lower() == vid_lower or
            v.get("base_voice", "").lower() == vid_lower or
            v.get("name", "").lower() == vid_lower or
            vid_lower.replace("kokoro-", "") == v.get("id", "").lower() or
            vid_lower.replace("gemini-", "") == v.get("id", "").lower()
        ):
            return v
    # Check custom voices
    if VOICES_FILE.exists():
        try:
            with open(VOICES_FILE, "r", encoding="utf-8") as f:
                custom_voices = json.load(f)
                for cv in custom_voices:
                    if cv.get("id", "").lower() == vid_lower:
                        return cv
        except Exception:
            pass

    return NEURAL_VOICES[0]

def load_history() -> List[Dict[str, Any]]:
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def add_history_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    history = load_history()
    if "id" not in entry:
        entry["id"] = str(uuid.uuid4())
    if "created_at" not in entry:
        entry["created_at"] = time.time()
    history.insert(0, entry)
    # keep last 100 entries
    history = history[:100]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)
    return entry

def delete_history_entry(entry_id: str) -> bool:
    history = load_history()
    filtered = [h for h in history if h.get("id") != entry_id]
    if len(filtered) != len(history):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(filtered, f, indent=2)
        return True
    return False
