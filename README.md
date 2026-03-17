# nova

free, open-source holographic AI assistant for macOS.

anime-styled avatar. local LLM. real system integration. zero cost.

![screenshot](docs/screenshot.png)

## what it does

NOVA is a desktop AI assistant with a holographic anime-styled avatar rendered in real-time. she runs entirely on your Mac, talks to you through macOS text-to-speech, and can actually control your system. open apps, check battery, set volume, manage clipboard.

the holographic effect uses custom GLSL shaders: Fresnel edge glow, scrolling scanlines, floating particles, wireframe overlay, orbital rings. the avatar tracks your mouse cursor and transitions between animation states (thinking, speaking, idle).

powered by Ollama for local LLM inference. no cloud. no API keys. no cost.

## prerequisites

- macOS (Apple Silicon recommended)
- [Rust](https://rustup.rs)
- [Node.js](https://nodejs.org) + pnpm
- [Ollama](https://ollama.ai) with a model pulled (`ollama pull llama3.1:8b`)
- [Blender](https://blender.org) (only if regenerating the 3D head mesh)

## quick start

```bash
# make sure Ollama is running
ollama serve &
ollama pull llama3.1:8b

# clone and run
git clone https://github.com/StressTestor/nova.git
cd nova
pnpm install
cargo tauri dev
```

press `Cmd+Shift+N` to toggle NOVA from anywhere.

## system commands

NOVA handles these directly without touching the LLM:

| command | what it does |
|---------|-------------|
| `open [app]` | launches an app |
| `set volume to [0-100]` | changes system volume |
| `what's my battery` | shows battery percentage |
| `system info` | memory, disk, uptime |
| `clipboard` | shows clipboard contents |
| `goodnight` | power-down animation, minimizes to tray |

everything else goes to your local LLM.

## tech stack

| component | technology |
|-----------|-----------|
| app shell | Tauri 2 |
| backend | Rust |
| frontend | Three.js + custom GLSL |
| bundler | Vite |
| local LLM | Ollama |
| TTS | macOS `say` |
| system control | AppleScript (whitelisted templates) |

## roadmap

- v0.2: voice input (STT), real audio lip-sync, webcam face tracking
- v0.3: plugin system for community integrations
- v0.4: custom avatar support (bring your own .glb)
- v1.0: Linux support

## build from source

```bash
pnpm install
cargo tauri build
# output: src-tauri/target/release/bundle/dmg/NOVA_0.1.0_aarch64.dmg
```

## regenerate head mesh

```bash
blender --background --python scripts/generate_holo_head_anime.py
mv scripts/holo_head.glb src/assets/models/holo_head.glb
```

## license

MIT
