# Livepaper 🎬

A polished video wallpaper manager for **KDE Plasma 6**, built on top of [Smart Video Wallpaper Reborn](https://github.com/luisbocanegra/plasma-smart-video-wallpaper-reborn).

Livepaper provides a clean, one-click desktop app to manage video wallpapers — no terminal commands or manual config editing required.

## Features

- 🖼 **Wallpaper library** — Grid view with auto-generated thumbnails
- 🖥 **Desktop & lock screen** — Apply videos to either or both in one click
- ⚙ **Full settings** — All plugin options exposed in one place:
  - Positioning / fill mode (Stretch, Fit, Fill, Tile)
  - Playback speed, alternative speed, volume, mute
  - Random order, resume last position, per-video timer
  - Cross-fade transition between videos (Beta)
  - Pause conditions (never, maximized/fullscreen, active window, window present, desktop effect)
  - Blur conditions + radius + animation duration
  - Battery saver with configurable threshold
  - Per-monitor window detection
- 🔍 **Setup wizard** — First-run check for plugin, Plasma version, and codecs
- 📺 **Multi-monitor** — Apply to all screens or a specific screen

## Installation

### Arch Linux (AUR)

```bash
paru -S livepaper
```

This installs the plugin, codecs, and Livepaper in one shot.

### From source

```bash
git clone https://github.com/VachanShetty95/livepaper.git
cd livepaper
pip install -e .
livepaper
```

**Dependencies:** Python ≥ 3.11, PyQt6, Pydantic v2, KDE Plasma 6,
`plasma6-wallpapers-smart-video-wallpaper-reborn`, `qt6-multimedia-ffmpeg`, `ffmpeg`

## How it works

Livepaper does **not** render video itself. It orchestrates the existing plugin:

- **Desktop wallpaper** — `qdbus6 org.kde.plasmashell /PlasmaShell evaluateScript` with the
  full plugin ID (`luisbocanegra.smart.video.wallpaper.reborn`) and all config keys
- **Lock screen** — writes `~/.config/kscreenlockerrc` with matching plugin ID and settings
- **Settings** — stored in `~/.config/livepaper/config.json`
- **Thumbnails** — cached in `~/.cache/livepaper/thumbnails/` via `ffmpeg`

## Development

```bash
pip install -e ".[dev]"
pytest --cov=src/livepaper -v
ruff check src/ tests/
bandit -r src/livepaper/
```

## Credits

- **Smart Video Wallpaper Reborn** by [Luis Bocanegra](https://github.com/luisbocanegra)
- **Livepaper** by [Vachan Shetty](https://github.com/VachanShetty95)

## License

MIT — see [LICENSE](LICENSE).
