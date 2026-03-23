"""Configuration manager for Livepaper and KDE config files."""

from __future__ import annotations

import configparser
import json
from pathlib import Path

from livepaper.models import AppConfig, WallpaperEntry

# Default paths
APP_CONFIG_DIR = Path.home() / ".config" / "livepaper"
APP_CONFIG_FILE = APP_CONFIG_DIR / "config.json"
KSCREENLOCKER_CONFIG = Path.home() / ".config" / "kscreenlockerrc"


def _ensure_config_dir(config_dir: Path | None = None) -> Path:
    """Ensure the config directory exists and return its path."""
    target = config_dir or APP_CONFIG_DIR
    target.mkdir(parents=True, exist_ok=True)
    return target


def read_app_config(config_file: Path | None = None) -> AppConfig:
    """Read application config from JSON file.

    Returns default config if file doesn't exist or is invalid.
    """
    target = config_file or APP_CONFIG_FILE

    if not target.exists():
        return AppConfig()

    try:
        data = json.loads(target.read_text(encoding="utf-8"))
        return AppConfig.model_validate(data)
    except (json.JSONDecodeError, ValueError):
        return AppConfig()


def write_app_config(config: AppConfig, config_file: Path | None = None) -> None:
    """Write application config to JSON file."""
    target = config_file or APP_CONFIG_FILE
    _ensure_config_dir(target.parent)

    target.write_text(
        config.model_dump_json(indent=2),
        encoding="utf-8",
    )


def apply_lock_screen_wallpaper(
    video_paths: list[Path],
    kscreenlocker_path: Path | None = None,
) -> None:
    """Edit kscreenlockerrc to set the lock screen video wallpaper.

    This modifies the [Greeter][Wallpaper][smart-video-wallpaper-reborn][General]
    section of the kscreenlockerrc config file.
    """
    config_path = kscreenlocker_path or KSCREENLOCKER_CONFIG

    parser = configparser.ConfigParser()
    parser.optionxform = str  # Preserve case (KDE configs are case-sensitive)

    if config_path.exists():
        parser.read(str(config_path), encoding="utf-8")

    # Set the wallpaper plugin for the greeter (lock screen)
    greeter_section = "Greeter"
    if not parser.has_section(greeter_section):
        parser.add_section(greeter_section)
    parser.set(greeter_section, "WallpaperPlugin", "smart-video-wallpaper-reborn")

    # Set video URLs in the plugin config section
    plugin_section = "Greeter][Wallpaper][smart-video-wallpaper-reborn][General"
    if not parser.has_section(plugin_section):
        parser.add_section(plugin_section)

    urls = ",".join(f"file://{p.resolve()}" for p in video_paths)
    parser.set(plugin_section, "VideoUrls", urls)

    # Write back
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        parser.write(f)


def add_wallpapers_to_library(
    new_paths: list[Path],
    config_file: Path | None = None,
) -> AppConfig:
    """Add video files to the wallpaper library."""
    config = read_app_config(config_file)

    existing_paths = {w.path for w in config.wallpapers}
    new_entries = [
        WallpaperEntry(path=p)
        for p in new_paths
        if p.resolve() not in existing_paths and p.exists()
    ]

    updated_wallpapers = list(config.wallpapers) + new_entries
    updated_config = config.model_copy(update={"wallpapers": updated_wallpapers})

    write_app_config(updated_config, config_file)
    return updated_config


def remove_wallpaper_from_library(
    path: Path,
    config_file: Path | None = None,
) -> AppConfig:
    """Remove a wallpaper from the library by path."""
    config = read_app_config(config_file)

    resolved = path.resolve()
    updated_wallpapers = [w for w in config.wallpapers if w.path.resolve() != resolved]
    updated_config = config.model_copy(update={"wallpapers": updated_wallpapers})

    write_app_config(updated_config, config_file)
    return updated_config
