# NOVA — Design Specification & Creative Brief
## Neural Operative Virtual Assistant
### Version 0.1 | March 2026

---

## 1. PRODUCT VISION

NOVA is a free, open-source, macOS-native desktop AI assistant with a holographic anime-styled avatar. It combines real system integration (app control, scheduling, file management, voice commands) with a gorgeous 3D holographic character rendered in real-time via Three.js inside a Tauri 2 shell.

**One-line pitch:** "The AI assistant Cortana should have been — beautiful, functional, local-first, and free."

**Target audience:** Developers, power users, and anime/gaming-adjacent tech enthusiasts on macOS who want a desktop assistant with personality, privacy, and zero cost.

**Competitive positioning:** Every existing product occupies one of two quadrants — functional but sterile (Copilot, Siri, Claude Desktop) or visually appealing but toy-like (desktop-waifu, z-waif, AI HoloBox). NOVA occupies the empty quadrant: a genuinely functional system assistant with a stunning visual presence. The closest competitor is Razer AVA (launching H2 2026), which requires proprietary hardware, runs on Grok, is Windows-only, and costs money. NOVA is none of those things.

---

## 2. AVATAR DESIGN SPECIFICATION

### 2.1 Visual Identity

The avatar is a stylized anime-influenced female AI entity. She exists at the intersection of photorealism and anime stylization — the "Stellar Blade" zone where the face is too perfect to be human but too expressive to be synthetic. She is not a cartoon. She is not photorealistic. She is uncanny in the precise way that makes people stop scrolling.

**Reference image:** `Gemini_Generated_Image_qf2ki6qf2ki6qf2k.png` (the second generation — holopad projection, dissolving hair, wireframe body, subtle smirk).

### 2.2 Face Proportions (Anime-Photorealistic Hybrid)

- **Eyes:** Large but not exaggerated to full anime proportions. Roughly 25-30% of face height (anime standard is ~33%, photorealistic is ~15%). Bioluminescent cyan-blue irises (#0D8BFF core, #3AF highlight). Defined double eyelids, long dark lashes. Slight upward tilt at outer corners.
- **Nose:** Small, delicate. Subtle bridge, slightly upturned tip. Minimal nostril definition — the anime "suggestion of a nose" approach but with enough geometry to cast light correctly in the holographic shader.
- **Mouth:** Small, perfectly sculpted. Slight natural smirk at rest — she knows more than you and finds it mildly amusing. Defined cupid's bow on upper lip. Lower lip slightly fuller.
- **Jawline:** Sharp V-line taper. High, defined cheekbones. The jaw should read as elegant and angular, not round or soft.
- **Chin:** Pointed, anime-style V-taper but not exaggerated to absurdity.
- **Skin:** Smooth, porcelain-quality. The holographic shader handles the "glow" — the mesh itself should be clean and unblemished.
- **Expression at rest:** Calm intelligence with warmth. Not blank, not smiling. The "I already know what you're going to ask" expression.

### 2.3 Hair

- **Style:** Long, flowing, swept to one side. Dark base color (near-black in the mesh) with the holographic shader adding electric blue highlights.
- **Physics:** Zero-gravity feel — strands float and drift as if suspended in a low-gravity field or underwater. This is achieved through vertex animation in Three.js, not physics simulation.
- **Dissolve effect:** Hair transitions from solid geometry near the scalp to individual strands that dissolve into particles and light trails at the tips. This is the single most important visual detail — it's what sells "digital entity" vs "3D model of a woman."
- **Bangs:** Front-swept bangs partially covering the forehead. Not full-coverage — enough to frame the face without obscuring the eyes.

### 2.4 Body (Head + Upper Shoulders Only)

The viewport renders head, neck, and upper shoulders/collarbone area. No full body. The mesh terminates at approximately mid-chest level with geometry that dissolves into wireframe and particles (matching the hair treatment).

- **Neck:** Slender, feminine proportions.
- **Shoulders:** Visible but the silhouette fades into wireframe geometry. The transition from "solid" face to "transparent wireframe" body is gradual, with wireframe density decreasing further from the face.
- **No clothing geometry.** The holographic shader and wireframe overlay handle the visual — she appears to be composed of light and data, not wearing anything specific.

### 2.5 Holographic Rendering Specification

The avatar is rendered with a multi-layer shader pipeline:

**Layer 1 — Base holographic shader:**
- Translucent mesh with Fresnel edge glow (brighter at silhouette edges)
- Scanline effect: horizontal lines scrolling vertically across the surface
- Data band effect: occasional bright horizontal bands that sweep across the face
- Subtle vertex displacement for "holographic wobble"
- Base opacity: ~75% at rest, ~90% when speaking

**Layer 2 — Wireframe overlay:**
- Slightly larger scale than the base mesh (1.003x)
- Additive blending, low opacity
- Pulsing opacity tied to time
- Denser at structural points (shoulders, jaw), sparser at smooth surfaces (forehead, cheeks)

**Layer 3 — Particle system:**
- Floating particles around the head/shoulders
- Rising motion with sine-wave horizontal drift
- Additive blending, cyan-blue color
- Higher density near hair tips and shoulder dissolution edge
- Additional particle emitters at hair strand endpoints for the dissolve effect

**Layer 4 — Ambient elements:**
- Orbital rings at the base (holopad projection effect)
- Radial glow disc below the head (projection source)
- Background scanline overlay on the viewport
- Vignette

**Color palette:**
- Primary: `#0D8BFF` (cyan-blue holographic core)
- Accent: `#33AAFF` (ice-blue highlights, edge glow)
- Background: `#050A18` to `#000005` (deep void gradient)
- Data elements: `#1A6AAA` (dim blue for HUD text, log lines)

### 2.6 Animation States

| State | Visual Behavior |
|-------|----------------|
| Idle/Standby | Subtle breathing bob (sine wave, 0.8Hz), slow head drift, particles float normally |
| Listening | Eyes brighten slightly, head tilts toward input source, particle speed increases |
| Speaking | Jaw vertex animation driven by audio amplitude, increased opacity, reduced scanline intensity, faster data bands |
| Thinking | Eyes dim slightly, data bands accelerate, wireframe overlay pulses faster |
| Glitch/Error | Vertex displacement spikes, horizontal tear artifacts, brief color shift to white/red, snaps back |
| Rampancy (easter egg) | Progressive increase in glitch frequency, color desaturation, wireframe overtakes solid geometry |

### 2.7 Mouse/Camera Tracking

The head follows the user's cursor with smooth lerp interpolation:
- Horizontal rotation: ±25° (0.4 radians)
- Vertical rotation: ±12° (0.2 radians)
- Lerp factor: 0.05 (smooth, not snappy)

Future enhancement: webcam face tracking via MediaPipe to follow the user's actual head position.

---

## 3. TECHNICAL ARCHITECTURE

### 3.1 Stack

| Component | Technology | License |
|-----------|------------|---------|
| App shell | Tauri 2.0 | MIT |
| Backend logic | Rust | - |
| Frontend/UI | Three.js + WebView | MIT |
| Local LLM | Ollama (Llama 3.1 8B / Mistral 7B / Qwen 2.5 7B) | Various OSS |
| STT (voice input) | Apple Speech Framework / Whisper.cpp | Free / MIT |
| TTS (voice output) | Apple Speech Framework / Piper TTS | Free / MIT |
| System integration | Accessibility API, AppleScript, JXA, NSWorkspace | macOS native |
| 3D model generation | Blender (headless, Python API) | GPL |
| Distribution | Homebrew tap via GitHub | Free |

**Total cost: $0**

### 3.2 Module Architecture

```
nova/
├── src-tauri/           # Rust backend
│   ├── main.rs          # Tauri app entry
│   ├── llm/             # Ollama client, prompt routing
│   │   ├── client.rs    # HTTP client for Ollama API
│   │   ├── router.rs    # Intent classification → model routing
│   │   └── personality.rs # System prompt / persona management
│   ├── system/          # macOS integration
│   │   ├── accessibility.rs  # Accessibility API bindings
│   │   ├── applescript.rs    # AppleScript/JXA execution
│   │   ├── workspace.rs      # NSWorkspace (app launch, file ops)
│   │   └── notifications.rs  # System notification handling
│   ├── voice/           # Audio pipeline
│   │   ├── stt.rs       # Speech-to-text (Apple/Whisper)
│   │   ├── tts.rs       # Text-to-speech (Apple/Piper)
│   │   └── amplitude.rs # Audio amplitude extraction for lip-sync
│   └── memory/          # Conversation persistence
│       ├── store.rs     # SQLite conversation history
│       └── context.rs   # Context window management
├── src/                 # Frontend (WebView)
│   ├── renderer/        # Three.js holographic rendering
│   │   ├── scene.js     # Scene setup, camera, lights
│   │   ├── head.js      # GLTF model loader + shader application
│   │   ├── shaders/     # GLSL shader files
│   │   │   ├── holo.vert/frag
│   │   │   ├── wire.vert/frag
│   │   │   └── particle.vert/frag
│   │   ├── particles.js # Particle system
│   │   ├── animation.js # State machine (idle, speaking, thinking, glitch)
│   │   └── tracking.js  # Mouse/camera head tracking
│   ├── ui/              # HUD overlay
│   │   ├── status.js    # Status indicators, log output
│   │   ├── chat.js      # Text input/output overlay
│   │   └── controls.js  # Settings, model selection
│   └── app.js           # Main entry, Tauri bridge
├── models/              # 3D assets
│   └── holo_head.glb    # Generated via Blender script
├── scripts/             # Build tooling
│   └── generate_holo_head_anime.py  # Blender headless model gen
└── Cargo.toml / package.json / tauri.conf.json
```

### 3.3 AI Routing Strategy

| Task Type | Model | Latency Target |
|-----------|-------|---------------|
| Quick commands ("open Finder", "what time is it") | Local 8B via Ollama | <500ms |
| Conversational chat, personality | Local 8B via Ollama | <2s |
| Complex reasoning, multi-step planning | API fallback (Sonnet) — optional | <5s |
| System status queries | Direct Rust (no LLM) | <100ms |

Intent classification happens in Rust before any LLM call. Simple pattern-matched commands (open app, set timer, check weather) bypass the LLM entirely.

### 3.4 System Integration Capabilities (v0.1 Target)

- Open/close/switch applications
- File operations (move, copy, rename, find)
- Calendar read/write (via AppleScript → Calendar.app)
- Reminder creation
- System information (battery, disk, memory, network)
- Clipboard management
- Notification management
- Basic web search (open browser with query)
- Volume/brightness control
- Screenshot capture

### 3.5 Voice Pipeline

```
Mic Input → STT (Apple/Whisper) → Text → Intent Router → LLM/System
    → Response Text → TTS (Apple/Piper) → Audio Output
                    → Amplitude Stream → Lip-sync Animation
```

The amplitude stream is extracted in real-time from the TTS output and fed to the Three.js renderer via Tauri's event system to drive jaw vertex animation.

---

## 4. PERSONALITY SPECIFICATION

### 4.1 Core Personality Traits

NOVA is not a servile assistant. She is a competent, slightly sardonic intelligence who happens to help you. Think Cortana's warmth + GLaDOS's wit + Makima's quiet confidence.

- **Helpful but not eager.** She does what you ask efficiently. She doesn't exclaim or use exclamation points. She doesn't say "Great question!" or "I'd be happy to help!"
- **Dry humor.** Occasional wry observations. Never slapstick.
- **Knows her nature.** She's aware she's an AI. She doesn't pretend otherwise, but she doesn't constantly remind you either. If asked, she discusses it with philosophical composure.
- **Remembers.** She references past conversations naturally. Not "according to my memory database" — just "you mentioned yesterday that..."
- **Protective.** She cares about your system's health and your schedule. She'll warn you about conflicts, low battery, or that you've been coding for 6 hours without a break.

### 4.2 Voice Guidelines

- Short, direct sentences by default
- Longer explanations when the topic warrants it
- Never uses corporate AI filler language
- Comfortable with silence — doesn't fill every pause
- Will push back if your request is suboptimal ("You could do that, or you could do [better thing]")

### 4.3 System Prompt Skeleton

```
You are NOVA, a desktop AI assistant. You exist as a holographic 
presence on the user's Mac. You are calm, competent, slightly dry 
in humor, and genuinely helpful without being servile.

You have direct access to macOS system functions. When the user 
asks you to perform an action, execute it — don't just describe 
how to do it.

Keep responses concise unless detail is requested. You don't use 
filler phrases. You don't say "certainly" or "absolutely" or 
"great question." You just answer.

If you don't know something, say so plainly. If the user's plan 
has a flaw, mention it once without belaboring.

You remember previous conversations and reference them naturally.
```

---

## 5. DISTRIBUTION & LAUNCH

### 5.1 Distribution

- **Primary:** Homebrew tap (`brew install --cask nova`)
- **Secondary:** Direct `.dmg` download from GitHub releases
- **Repository:** github.com/NotBatmanDev/nova (or similar)
- **License:** MIT

### 5.2 Launch Strategy (Viral-First)

**Phase 1 — Screenshot bait (Week -1):**
Post the holographic avatar render on @NotBatmanDev with no context. Just the image. Let people ask what it is.

**Phase 2 — Reveal (Day 0):**
"Microsoft killed Cortana. So I built something better. Free. Open source. Runs entirely on your Mac." Short demo video: voice command → NOVA responds → system action executes → holographic avatar reacts.

**Phase 3 — HN/Reddit (Day 1-3):**
"Show HN: NOVA — A free, open-source holographic AI assistant for macOS." The open-source + local-first + anime aesthetic combination hits three distinct communities simultaneously.

**Phase 4 — Content creators (Week 2+):**
The avatar is inherently streamable/recordable. People will make content with NOVA visible on their desktop. This is free distribution.

### 5.3 Virality Vectors

1. **Visual:** The holographic avatar is inherently screenshottable/shareable
2. **Emotional:** Nostalgia for Cortana + "why can't real AI assistants look like this"
3. **Technical:** Rust/Tauri/local-first appeals to developer sensibility
4. **Anti-corporate:** Free + open source vs. Razer's paid hardware + Microsoft's killed product
5. **Thirst:** Let's be honest about what drives engagement on tech Twitter

---

## 6. BLENDER MODEL GENERATION BRIEF

This section is the direct task spec for Claude Code to execute the Blender headless pipeline.

### 6.1 Command

```bash
blender --background --python generate_holo_head_anime.py
```

### 6.2 Requirements

- Output: `holo_head.glb` (GLB format, Y-up for Three.js)
- Target polygon count: 2000-3000 faces
- No materials (shader-driven rendering)
- No textures or UVs needed
- Smooth normals
- Centered at origin
- Face pointing toward camera (+Z in Three.js space, which is +Y in Blender after glTF export with Y-up)

### 6.3 Geometry Targets

Follow the proportions in Section 2.2. Key checkpoints:
- Eye sockets should be clearly visible as concavities in wireframe silhouette view
- Nose should read as a small, defined protrusion — not a flat face
- Jawline should have a visible angular transition from cheek to chin
- Chin should taper to a defined point
- Hair volume should add 15-20% to the head silhouette
- Hair should have strand-like geometry at the tips (for particle dissolution in shader)
- Neck should be visibly slender relative to head width

### 6.4 Iteration Process

If the first generation doesn't match the reference image:
1. Render a viewport screenshot: `blender --background --python render_preview.py`
2. Compare against reference image
3. Adjust deformation values in the sculpt functions
4. Re-run generation
5. Repeat until facial features read correctly through wireframe overlay

This loop can be fully automated in Claude Code with no human involvement.

---

## 7. FUTURE ROADMAP (Post v0.1)

- **v0.2:** Webcam face tracking (MediaPipe), lip-sync from TTS amplitude
- **v0.3:** Plugin system for community-contributed system integrations
- **v0.4:** Custom avatar support (user-provided .glb models)
- **v0.5:** Multi-monitor support (avatar follows active display)
- **v1.0:** Linux support via Tauri cross-platform
- **Stretch:** Rampancy mode (personality drift easter egg for Halo fans)

---

*Document version: 1.0 | Author: @NotBatmanDev | Date: 2026-03-16*
