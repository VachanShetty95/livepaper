"""Configuration manager for Livepaper and KDE config files."""

from __future__ import annotations

import configparser
import json
from pathlib import Path

from livepaper.models import AppConfig, WallpaperEntry
from livepaper.services.dbus_client import PLUGIN_ID

APP_CONFIG_DIR = Path.home() / ".config" / "livepaper"
APP_CONFIG_FILE = APP_CONFIG_DIR / "config.json"
KSCREENLOCKER_CONFIG = Path.home() / ".config" / "kscreenlockerrc"


def _ensure_config_dir(config_dir: Path | None = None) -> Path:
    target = config_dir or APP_CONFIG_DIR
    target.mkdir(parents=True, exist_ok=True)
    return target


def read_app_config(config_file: Path | None = None) -> AppConfig:
    """Read application config from JSON. Returns defaults if missing/corrupt."""
    target = config_file or APP_CONFIG_FILE
    if not target.exists():
        return AppConfig()
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
        return AppConfig.model_validate(data)
    except (json.JSONDecodeError, ValueError):
        return AppConfig()


def write_app_config(config: AppConfig, config_file: Path | None = None) -> None:
    """Write application config to JSON."""
    target = config_file or APP_CONFIG_FILE
    _ensure_config_dir(target.parent)
    target.write_text(config.model_dump_json(indent=2), encoding="utf-8")


def apply_lock_screen_wallpaper(
    video_paths: list[Path],
    config: AppConfig | None = None,
    kscreenlocker_path: Path | None = None,
) -> None:
    """Edit kscreenlockerrc to configure the lock screen video wallpaper.

    KDE uses nested bracket sections like [Greeter][Wallpaper][plugin.id][General].
    Python's configparser treats the whole string as one section name, which
    writes the nested brackets correctly on disk.

    All plugin settings from AppConfig are written so the lock screen matches
    the desktop wallpaper configuration.
    """
    config_path = kscreenlocker_path or KSCREENLOCKER_CONFIG

    parser = configparser.ConfigParser()
    parser.optionxform = str  # Preserve case — KDE configs are case-sensitive

    if config_path.exists():
        parser.read(str(config_path), encoding="utf-8")

    # Set the wallpaper plugin for the greeter
    greeter_section = "Greeter"
    if not parser.has_section(greeter_section):
        parser.add_section(greeter_section)
    parser.set(greeter_section, "WallpaperPlugin", PLUGIN_ID)

    # Nested section — configparser writes it as [Greeter][Wallpaper][...][General]
    plugin_section = f"Greeter][Wallpaper][{PLUGIN_ID}][General"
    if not parser.has_section(plugin_section):
        parser.add_section(plugin_section)

    # Video URLs
    urls = ",".join(f"file://{p.resolve()}" for p in video_paths)
    parser.set(plugin_section, "VideoUrls", urls)

    # Apply all settings if config is provided
    if config:
        vc = config.video
        pc = config.playback
        parser.set(plugin_section, "FillMode", str(vc.fill_mode.value))
        parser.set(plugin_section, "PauseMode", str(vc.pause_mode.value))
        parser.set(plugin_section, "BlurMode", str(vc.blur_mode.value))
        parser.set(plugin_section, "BlurRadius", str(vc.blur_radius))
        parser.set(plugin_section, "BlurAnimationDuration", str(vc.blur_animation_duration))
        parser.set(plugin_section, "BlurOnOriginalProportions",
                   "true" if vc.blur_on_original_proportions else "false")
        parser.set(plugin_section, "BatterySaverEnabled",
                   "true" if vc.battery_saver_enabled else "false")
        parser.set(plugin_section, "BatteryThreshold", str(vc.battery_threshold))
        parser.set(plugin_section, "MuteAudio", "true" if pc.mute_audio else "false")
        parser.set(plugin_section, "Volume", str(pc.volume))
        parser.set(plugin_section, "PlaybackRate", str(pc.playback_rate))
        parser.set(plugin_section, "PlaybackRateAlt", str(pc.playback_rate_alt))
        parser.set(plugin_section, "RandomOrder", "true" if pc.random_order else "false")
        parser.set(plugin_section, "ResumeTime", "true" if pc.resume_time else "false")
        parser.set(plugin_section, "Timer", str(pc.timer))
        parser.set(plugin_section, "FadeEnabled", "true" if pc.fade_enabled else "false")
        parser.set(plugin_section, "FadeDuration", str(pc.fade_duration))

    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        parser.write(f)


def add_wallpapers_to_library(
    new_paths: list[Path],
    config_file: Path | None = None,
) -> AppConfig:
    """Add video files to the wallpaper library (deduplicates by path)."""
    config = read_app_config(config_file)
    existing = {w.path for w in config.wallpapers}
    new_entries = [
        WallpaperEntry(path=p)
        for p in new_paths
        if p.resolve() not in existing and p.exists()
    ]
    updated = config.model_copy(update={"wallpapers": list(config.wallpapers) + new_entries})
    write_app_config(updated, config_file)
    return updated


def remove_wallpaper_from_library(
    path: Path,
    config_file: Path | None = None,
) -> AppConfig:
    """Remove a wallpaper from the library by path."""
    config = read_app_config(config_file)
    resolved = path.resolve()
    updated = config.model_copy(
        update={"wallpapers": [w for w in config.wallpapers if w.path.resolve() != resolved]}
    )
    write_app_config(updated, config_file)
    return updated
