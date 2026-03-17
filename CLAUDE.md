## nova

holographic AI assistant for macOS. Tauri 2 + Rust backend, Three.js + GLSL frontend, Ollama for local LLM.

### commands

```bash
export PATH="/Volumes/onn/.cargo-root/bin:$PATH"
export CARGO_TARGET_DIR="/Volumes/onn/.cargo-tmp"

cargo tauri dev          # dev server (Vite + Tauri)
cargo tauri build        # production build -> .dmg
cd src-tauri && cargo test  # run Rust tests

pnpm install             # install frontend deps
pnpm dev                 # Vite dev server only (no Tauri)

blender --background --python scripts/generate_holo_head_anime.py  # regenerate head mesh
```

### architecture

```
src/                    # frontend (Vite + Three.js)
  main.js               # app entry
  constants.js          # shared colors, states, shader params
  renderer/             # Three.js holographic rendering
    scene.js            # scene setup, camera, render loop
    head.js             # GLTF loader, shader material application
    particles.js        # floating particle system
    ambient.js          # orbital rings, glow disc
    animation.js        # state machine -> shader uniform mapping
    tracking.js         # mouse -> head rotation
  shaders/              # GLSL (imported via vite-plugin-glsl)
    holo.vert/frag      # main holographic shader
    wire.vert/frag      # wireframe overlay
    particle.vert/frag  # particle system
    fallback.frag       # fallback if main shader fails
  ui/
    hud.js              # status display, log area, drag region
    chat.js             # input handling, Tauri IPC bridge

src-tauri/src/          # Rust backend
  lib.rs                # Tauri command registrations, app setup
  state.rs              # NovaState enum, AppState with abort handle
  llm/
    client.rs           # Ollama HTTP streaming client
    router.rs           # declarative intent router (pattern -> action)
    personality.rs      # system prompt
  system/
    applescript.rs      # osascript execution (template-based)
    workspace.rs        # app launching (open -a)
    info.rs             # battery, memory, disk, uptime via sysinfo
  voice/
    tts.rs              # macOS say command + phoneme jaw animation
```

### key decisions

- state machine lives in Rust, frontend reflects via Tauri events
- intent router uses declarative command table, NOT freeform LLM -> AppleScript
- AppleScript params validated with allowlist regex before execution
- shader fallback exists for GLSL compile failures
- render loop pauses on visibilitychange (zero GPU when hidden)
- stream overlap: cancel-and-replace (abort in-flight Ollama stream)

### gotchas

- tauri-cli is at `/Volumes/onn/.cargo-root/bin/cargo-tauri`, not in default PATH
- CARGO_TARGET_DIR should be `/Volumes/onn/.cargo-tmp` to avoid filling the boot drive
- Blender is only needed for model regeneration, not runtime
- Ollama must be running separately (`ollama serve`)
- transparent window requires `decorations: false` + `transparent: true` in tauri.conf.json
