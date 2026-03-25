"""DBus client for KDE Plasma wallpaper control.

The critical plugin ID is: luisbocanegra.smart.video.wallpaper.reborn
Using any other ID (e.g. 'smart-video-wallpaper-reborn') causes a silent
failure — plasmashell accepts the call but renders a black screen.
"""

from __future__ import annotations

import json
import shutil
import subprocess  # nosec B404
from pathlib import Path
from typing import TYPE_CHECKING, Any

from livepaper.models import BlurMode, PauseMode

if TYPE_CHECKING:
    from livepaper.models import PlaybackConfig, VideoConfig

# Exact plugin ID — must match metadata.json in the installed plugin
PLUGIN_ID = "luisbocanegra.smart.video.wallpaper.reborn"


class DBusError(Exception):
    """Raised when a DBus command fails."""


def _get_qdbus_binary() -> str:
    """Return the correct qdbus binary for the current Plasma version.

    Plasma 6 / Qt6 renames qdbus → qdbus6 on most distros.
    We try qdbus6 first (Plasma 6), then qdbus (Plasma 5 fallback).
    """
    for candidate in ("qdbus6", "qdbus-qt6", "qdbus"):
        if shutil.which(candidate):
            return candidate
    return "qdbus6"  # Let the subprocess fail with a clear error


def _sanitize_js_string(value: str) -> str:
    """Escape a generic string for safe use inside a JS string literal."""
    return value.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"')


def _split_timer(total_seconds: int) -> tuple[int, int, int]:
    seconds = max(0, total_seconds)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return hours, minutes, seconds


def _map_pause_mode(value: int) -> int:
    mapping = {
        PauseMode.NEVER.value: 3,
        PauseMode.MAXIMIZED_OR_FULLSCREEN.value: 0,
        PauseMode.ACTIVE_WINDOW.value: 1,
        PauseMode.WINDOW_PRESENT.value: 2,
        PauseMode.DESKTOP_EFFECT.value: 0,
    }
    return mapping.get(int(value), 0)


def _map_blur_mode(value: int) -> int:
    mapping = {
        BlurMode.NEVER.value: 5,
        BlurMode.ALWAYS.value: 4,
        BlurMode.MAXIMIZED_OR_FULLSCREEN.value: 0,
        BlurMode.ACTIVE_WINDOW.value: 1,
        BlurMode.WINDOW_PRESENT.value: 2,
        BlurMode.VIDEO_PAUSED.value: 3,
        BlurMode.DESKTOP_EFFECT.value: 5,
    }
    return mapping.get(int(value), 5)


def build_video_urls_value(
    video_paths: list[Path],
    playback_config: PlaybackConfig | None = None,
) -> str:
    """Build the plugin's JSON VideoUrls payload."""
    loop_current_video = bool(playback_config and playback_config.loop_current_video)
    videos = [
        {
            "filename": path.resolve().as_uri(),
            "enabled": True,
            "duration": 0,
            "customDuration": 0,
            "playbackRate": 0.0,
            "alternativePlaybackRate": 0.0,
            "loop": loop_current_video,
        }
        for path in video_paths
    ]
    return json.dumps(videos, separators=(",", ":"))


def build_plugin_config(
    video_config: VideoConfig | None = None,
    playback_config: PlaybackConfig | None = None,
) -> dict[str, Any]:
    """Return config values using the installed plugin's current schema."""
    vc = video_config
    pc = playback_config
    timer_hours, timer_minutes, timer_seconds = _split_timer(pc.timer if pc else 0)

    return {
        "FillMode": vc.fill_mode.value if vc else 2,
        "PauseMode": _map_pause_mode(vc.pause_mode.value) if vc else 0,
        "PauseBatteryLevel": vc.battery_threshold if vc else 20,
        "BatteryPausesVideo": vc.battery_saver_enabled if vc else True,
        "BatteryDisablesBlur": False,
        "BlurMode": _map_blur_mode(vc.blur_mode.value) if vc else 5,
        "BlurRadius": vc.blur_radius if vc else 40,
        "BlurAnimationDuration": vc.blur_animation_duration if vc else 300,
        "FillBlur": vc.blur_on_original_proportions if vc else True,
        "CheckWindowsActiveScreen": not vc.check_windows_from_all_screens if vc else True,
        "MuteMode": 5 if (pc and pc.mute_audio) else 4,
        "Volume": (pc.volume / 100) if pc else 1.0,
        "PlaybackRate": pc.playback_rate if pc else 1.0,
        "AlternativePlaybackRate": pc.playback_rate_alt if pc else 0.25,
        "RandomMode": pc.random_order if pc else False,
        "ResumeLastVideo": pc.resume_time if pc else False,
        "ChangeWallpaperMode": 2 if (pc and pc.timer > 0) else 1,
        "ChangeWallpaperTimerSeconds": timer_seconds,
        "ChangeWallpaperTimerMinutes": timer_minutes,
        "ChangeWallpaperTimerHours": timer_hours,
        "CrossfadeEnabled": pc.fade_enabled if pc else False,
        "CrossfadeDuration": pc.fade_duration if pc else 1000,
    }


def _build_wallpaper_script(
    video_paths: list[Path],
    screen_index: int = -1,
    video_config: VideoConfig | None = None,
    playback_config: PlaybackConfig | None = None,
) -> str:
    """Build the Plasma evaluateScript JS to fully configure the video wallpaper plugin.

    Sets the plugin, video URLs, and all user-configurable options so that
    applying from Livepaper is equivalent to configuring via the plugin's
    own settings UI.
    """
    urls_value = _sanitize_js_string(build_video_urls_value(video_paths, playback_config))
    config_values = build_plugin_config(video_config, playback_config)

    # The screen filter: -1 means apply to all desktops
    screen_filter = f"d.screen === {screen_index}" if screen_index >= 0 else "true"
    config_lines = "\n".join(
        f'        d.writeConfig("{key}", {json.dumps(value)});'
        for key, value in config_values.items()
    )

    script = f"""
var allDesktops = desktops();
for (var i = 0; i < allDesktops.length; i++) {{
    var d = allDesktops[i];
    if ({screen_filter}) {{
        d.wallpaperPlugin = "{PLUGIN_ID}";
        d.currentConfigGroup = Array("Wallpaper", "{PLUGIN_ID}", "General");
        d.writeConfig("VideoUrls", "{urls_value}");
{config_lines}
    }}
}}
""".strip()

    return script


def apply_desktop_wallpaper(
    video_paths: list[Path],
    screen_index: int = -1,
    video_config: VideoConfig | None = None,
    playback_config: PlaybackConfig | None = None,
) -> None:
    """Apply video wallpaper(s) to the desktop via Plasma's DBus evaluateScript API.

    Args:
        video_paths: List of video file paths to set as wallpaper.
        screen_index: Screen to apply to (-1 = all screens, 0+ = specific screen).
        video_config: VideoConfig with FillMode, pause/blur/battery settings.
        playback_config: PlaybackConfig with speed, volume, loop settings.

    Raises:
        DBusError: If the qdbus command fails or times out.
        FileNotFoundError: If any video file doesn't exist.
    """
    for p in video_paths:
        if not p.exists():
            msg = f"Video file not found: {p}"
            raise FileNotFoundError(msg)

    script = _build_wallpaper_script(video_paths, screen_index, video_config, playback_config)
    qdbus = _get_qdbus_binary()

    cmd = [
        qdbus,
        "org.kde.plasmashell",
        "/PlasmaShell",
        "org.kde.PlasmaShell.evaluateScript",
        script,
    ]

    try:
        result = subprocess.run(  # nosec B603
            cmd,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        if result.returncode != 0:
            msg = f"qdbus command failed (binary={qdbus}): {result.stderr.strip()}"
            raise DBusError(msg)
    except FileNotFoundError:
        msg = (
            f"'{qdbus}' not found. Install kde-cli-tools or qdbus-qt6."
        )
        raise DBusError(msg) from None
    except subprocess.TimeoutExpired:
        msg = "qdbus command timed out after 15s"
        raise DBusError(msg) from None


def get_evaluate_script_command(
    video_paths: list[Path],
    screen_index: int = -1,
    video_config: VideoConfig | None = None,
    playback_config: PlaybackConfig | None = None,
) -> list[str]:
    """Return the full qdbus command that would be executed (for testing/preview)."""
    script = _build_wallpaper_script(video_paths, screen_index, video_config, playback_config)
    qdbus = _get_qdbus_binary()
    return [
        qdbus,
        "org.kde.plasmashell",
        "/PlasmaShell",
        "org.kde.PlasmaShell.evaluateScript",
        script,
    ]
