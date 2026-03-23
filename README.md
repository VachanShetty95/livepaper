# Livepaper 🎬

A polished video wallpaper manager for **KDE Plasma 6**, built on top of [Smart Video Wallpaper Reborn](https://github.com/luisbocanegra/plasma-smart-video-wallpaper-reborn).

Livepaper provides a clean, one-click desktop app to manage video wallpapers — no terminal commands or manual config editing required.

## Features

- 🖼 **Wallpaper Library** — Grid view with auto-generated thumbnails
- 🖥 **Desktop & Lock Screen** — Apply videos to either or both
- ⚙ **Settings** — Pause on fullscreen, blur, battery saver, playback speed
- 🔍 **System Health Check** — First-run wizard verifies plugin, Plasma, and codecs
- 🎨 **System Theme** — Automatically adapts to your Breeze dark/light theme
- 📺 **Multi-Monitor** — Apply per-screen or all screens

## Installation

### Arch Linux (AUR)

```bash
paru -S livepaper
```

This will automatically install the required plugin and codecs.

### From Source

```bash
git clone https://github.com/VachanShetty95/livepaper.git
cd livepaper
pip install -e .
```

**Dependencies:**
- Python ≥ 3.11
- PyQt6
- Pydantic v2
- KDE Plasma 6
- [Smart Video Wallpaper Reborn](https://aur.archlinux.org/packages/plasma6-wallpapers-smart-video-wallpaper-reborn)
- `qt6-multimedia-ffmpeg`
- `ffmpeg` (for thumbnail generation)

## Usage

```bash
livepaper
```

Or launch from your application menu (Livepaper should appear under Settings).

### First Run

On first launch, the **Setup Wizard** checks your system:
- ✅ KDE Plasma 6 detected
- ✅ Smart Video Wallpaper plugin installed
- ✅ Media codecs available

If anything is missing, click **Fix** for guided installation.

### Adding Wallpapers

1. Click **Add Wallpaper** (or press `Ctrl+N`)
2. Select video files (`.mp4`, `.mkv`, `.webm`, `.avi`, `.mov`)
3. Click a wallpaper card to preview
4. Click **Apply to Desktop** or **Apply to Lock Screen**

## Development

```bash
# Install in dev mode
pip install -e ".[dev]"

# Run tests
pytest --cov=src/livepaper -v

# Lint
ruff check src/ tests/

# Security scan
bandit -r src/livepaper/
```

### Project Structure

```
src/livepaper/
├── __init__.py          # Package metadata
├── __main__.py          # App entry point
├── models/              # Pydantic data models
├── services/            # Backend logic
│   ├── system_detector.py
│   ├── dbus_client.py
│   ├── config_manager.py
│   ├── wallpaper_service.py
│   └── thumbnail_generator.py
└── ui/                  # PyQt6 interface
    ├── main_window.py
    ├── pages/
    │   ├── setup_wizard.py
    │   ├── library_view.py
    │   ├── settings_page.py
    │   └── about_page.py
    ├── widgets/
    │   └── wallpaper_card.py
    └── dialogs/
        └── add_wallpaper_dialog.py
```

## How It Works

Livepaper does **not** render video itself. It orchestrates the existing [Smart Video Wallpaper Reborn](https://github.com/luisbocanegra/plasma-smart-video-wallpaper-reborn) KDE plugin:

- **Desktop wallpaper:** Uses `qdbus org.kde.plasmashell /PlasmaShell evaluateScript` to set the wallpaper plugin and video paths
- **Lock screen:** Edits `~/.config/kscreenlockerrc` to configure the greeter wallpaper
- **Settings:** Stores app config in `~/.config/livepaper/config.json`
- **Thumbnails:** Cached in `~/.cache/livepaper/thumbnails/`

## License

MIT — see [LICENSE](LICENSE).

## Credits

- **Smart Video Wallpaper Reborn** by [Luis Bocanegra](https://github.com/luisbocanegra)
- **Livepaper** by [Vachan Shetty](https://github.com/VachanShetty95)
