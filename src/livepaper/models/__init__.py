"""Pydantic models for Livepaper configuration and data.

Config keys mirror the plugin's own config keys exactly so they can be
passed through verbatim to the DBus evaluateScript call.
"""

from __future__ import annotations

from enum import IntEnum, StrEnum
from pathlib import Path

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Enums matching the plugin's internal integer values
# ---------------------------------------------------------------------------

class FillMode(IntEnum):
    """Video fill/positioning mode — matches Qt VideoOutput fill modes used by plugin."""

    STRETCH = 0           # Stretch to fill, ignoring aspect ratio
    PRESERVE_ASPECT_FIT = 1   # Fit inside, letterboxed (black bars)
    PRESERVE_ASPECT_CROP = 2  # Fill and crop to preserve ratio (default)
    TILE = 3              # Tile the video
    TILE_VERTICAL = 4
    TILE_HORIZONTAL = 5

    @property
    def label(self) -> str:
        """Human-readable label for the UI."""
        return {
            FillMode.STRETCH: "Stretch",
            FillMode.PRESERVE_ASPECT_FIT: "Fit (keep proportions)",
            FillMode.PRESERVE_ASPECT_CROP: "Fill (crop to fit)",
            FillMode.TILE: "Tile",
            FillMode.TILE_VERTICAL: "Tile vertical",
            FillMode.TILE_HORIZONTAL: "Tile horizontal",
        }[self]


class PauseMode(IntEnum):
    """When to pause video playback — mirrors plugin PauseMode integer values."""

    NEVER = 0
    MAXIMIZED_OR_FULLSCREEN = 1
    ACTIVE_WINDOW = 2
    WINDOW_PRESENT = 3
    DESKTOP_EFFECT = 4

    @property
    def label(self) -> str:
        return {
            PauseMode.NEVER: "Never",
            PauseMode.MAXIMIZED_OR_FULLSCREEN: "Maximized or fullscreen window",
            PauseMode.ACTIVE_WINDOW: "Active window",
            PauseMode.WINDOW_PRESENT: "Window is present",
            PauseMode.DESKTOP_EFFECT: "Based on active desktop effect",
        }[self]


class BlurMode(IntEnum):
    """When to apply blur — mirrors plugin BlurMode integer values."""

    NEVER = 0
    ALWAYS = 1
    MAXIMIZED_OR_FULLSCREEN = 2
    ACTIVE_WINDOW = 3
    WINDOW_PRESENT = 4
    VIDEO_PAUSED = 5
    DESKTOP_EFFECT = 6

    @property
    def label(self) -> str:
        return {
            BlurMode.NEVER: "Never",
            BlurMode.ALWAYS: "Always",
            BlurMode.MAXIMIZED_OR_FULLSCREEN: "Maximized or fullscreen window",
            BlurMode.ACTIVE_WINDOW: "Active window",
            BlurMode.WINDOW_PRESENT: "Window is present",
            BlurMode.VIDEO_PAUSED: "Video is paused",
            BlurMode.DESKTOP_EFFECT: "Based on active desktop effect",
        }[self]


class MonitorMode(StrEnum):
    """How to apply wallpaper across monitors."""

    ALL = "all"
    PER_SCREEN = "per_screen"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

class WallpaperEntry(BaseModel):
    """A single video wallpaper in the library."""

    path: Path
    name: str = ""
    thumbnail_path: Path | None = None

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: Path) -> Path:
        resolved = v.resolve()
        if ".." in resolved.parts:
            msg = f"Path traversal not allowed: {v}"
            raise ValueError(msg)
        return resolved

    def model_post_init(self, __context: object) -> None:
        if not self.name:
            object.__setattr__(self, "name", self.path.stem)


class VideoConfig(BaseModel):
    """Settings that control how video is displayed and when it pauses/blurs.

    These map directly to the plugin's config keys.
    """

    # Positioning
    fill_mode: FillMode = FillMode.PRESERVE_ASPECT_CROP

    # Pause behaviour
    pause_mode: PauseMode = PauseMode.MAXIMIZED_OR_FULLSCREEN

    # Blur
    blur_mode: BlurMode = BlurMode.NEVER
    blur_radius: int = Field(default=40, ge=0, le=100)
    blur_animation_duration: int = Field(default=300, ge=0, le=5000)
    blur_on_original_proportions: bool = False

    # Battery saver
    battery_saver_enabled: bool = True
    battery_threshold: int = Field(default=20, ge=5, le=100)

    # Per-monitor window detection
    check_windows_from_all_screens: bool = False


class PlaybackConfig(BaseModel):
    """Settings that control video playback behaviour.

    These map directly to the plugin's config keys.
    """

    # Audio
    mute_audio: bool = False
    volume: int = Field(default=100, ge=0, le=100)

    # Speed
    playback_rate: float = Field(default=1.0, ge=0.1, le=4.0)
    playback_rate_alt: float = Field(default=0.25, ge=0.1, le=4.0)

    # Playlist
    random_order: bool = False
    resume_time: bool = False   # resume from last position on startup
    timer: int = Field(default=0, ge=0)   # seconds per video; 0 = off (use full length)

    # Cross-fade transition (Beta feature of the plugin)
    fade_enabled: bool = False
    fade_duration: int = Field(default=1000, ge=100, le=10000)


class AppConfig(BaseModel):
    """Full application config persisted to ~/.config/livepaper/config.json."""

    # Video display + smart features
    video: VideoConfig = Field(default_factory=VideoConfig)

    # Playback settings
    playback: PlaybackConfig = Field(default_factory=PlaybackConfig)

    # Lock screen sync
    sync_lock_screen: bool = False

    # Monitor targeting
    monitor_mode: MonitorMode = MonitorMode.ALL

    # Library
    wallpapers: list[WallpaperEntry] = Field(default_factory=list)

    # First-run flag
    first_run_complete: bool = False


# ---------------------------------------------------------------------------
# System check models (unchanged)
# ---------------------------------------------------------------------------

class SystemCheckItem(BaseModel):
    """Single item in the system health check."""

    name: str
    passed: bool
    message: str
    fix_url: str = ""


class SystemStatus(BaseModel):
    """Result of the system health check."""

    plasma_version: str = ""
    plasma_ok: bool = False
    plugin_installed: bool = False
    codecs_available: bool = False

    @property
    def all_checks_passed(self) -> bool:
        return self.plasma_ok and self.plugin_installed and self.codecs_available

    def to_check_items(self) -> list[SystemCheckItem]:
        return [
            SystemCheckItem(
                name="KDE Plasma 6",
                passed=self.plasma_ok,
                message=f"Version {self.plasma_version}" if self.plasma_ok else "Not detected",
                fix_url="https://kde.org/plasma-desktop/",
            ),
            SystemCheckItem(
                name="Smart Video Wallpaper Plugin",
                passed=self.plugin_installed,
                message="Installed" if self.plugin_installed else "Not installed",
                fix_url="https://aur.archlinux.org/packages/plasma6-wallpapers-smart-video-wallpaper-reborn",
            ),
            SystemCheckItem(
                name="Media codecs (qt6-multimedia-ffmpeg)",
                passed=self.codecs_available,
                message="Available" if self.codecs_available else "Missing — video will not play",
                fix_url="https://wiki.archlinux.org/title/Codecs_and_containers#Video_codecs",
            ),
        ]
