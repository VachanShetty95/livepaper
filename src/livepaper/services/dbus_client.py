"""DBus client for KDE Plasma wallpaper control.

The critical plugin ID is: luisbocanegra.smart.video.wallpaper.reborn
Using any other ID (e.g. 'smart-video-wallpaper-reborn') causes a silent
failure — plasmashell accepts the call but renders a black screen.
"""

from __future__ import annotations

import shutil
import subprocess  # nosec B404
from pathlib import Path
from typing import TYPE_CHECKING

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


def _sanitize_path(path: Path) -> str:
    """Sanitize a file path for safe use in JavaScript string literals."""
    resolved = str(path.resolve())
    return resolved.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"')


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
    urls_value = ",".join(f"file://{_sanitize_path(p)}" for p in video_paths)

    # Build config writes from provided config objects (with defaults matching plugin defaults)
    vc = video_config
    pc = playback_config

    fill_mode = vc.fill_mode.value if vc else 2          # 2 = PreserveAspectCrop (Stretch in Qt terms maps differently; plugin uses its own numbering)
    mute_audio = "true" if (pc and pc.mute_audio) else "false"
    volume = pc.volume if pc else 100
    playback_rate = pc.playback_rate if pc else 1.0
    playback_rate_alt = pc.playback_rate_alt if pc else 0.25
    random_order = "true" if (pc and pc.random_order) else "false"
    resume_time = "true" if (pc and pc.resume_time) else "false"
    timer = pc.timer if pc else 0
    fade_enabled = "true" if (pc and pc.fade_enabled) else "false"
    fade_duration = pc.fade_duration if pc else 1000

    pause_mode = vc.pause_mode.value if vc else 1          # 1 = Maximized/Fullscreen
    blur_mode = vc.blur_mode.value if vc else 0            # 0 = Never
    blur_radius = vc.blur_radius if vc else 40
    blur_anim_duration = vc.blur_animation_duration if vc else 300
    blur_on_original = "true" if (vc and vc.blur_on_original_proportions) else "false"

    battery_enabled = "true" if (vc and vc.battery_saver_enabled) else "false"
    battery_threshold = vc.battery_threshold if vc else 20

    check_all_screens = "true" if (vc and vc.check_windows_from_all_screens) else "false"

    # The screen filter: -1 means apply to all desktops
    screen_filter = f"d.screen === {screen_index}" if screen_index >= 0 else "true"

    script = f"""
var allDesktops = desktops();
for (var i = 0; i < allDesktops.length; i++) {{
    var d = allDesktops[i];
    if ({screen_filter}) {{
        d.wallpaperPlugin = "{PLUGIN_ID}";
        d.currentConfigGroup = Array("Wallpaper", "{PLUGIN_ID}", "General");
        d.writeConfig("VideoUrls", "{urls_value}");
        d.writeConfig("FillMode", {fill_mode});
        d.writeConfig("MuteAudio", {mute_audio});
        d.writeConfig("Volume", {volume});
        d.writeConfig("PlaybackRate", {playback_rate});
        d.writeConfig("PlaybackRateAlt", {playback_rate_alt});
        d.writeConfig("RandomOrder", {random_order});
        d.writeConfig("ResumeTime", {resume_time});
        d.writeConfig("Timer", {timer});
        d.writeConfig("FadeEnabled", {fade_enabled});
        d.writeConfig("FadeDuration", {fade_duration});
        d.writeConfig("PauseMode", {pause_mode});
        d.writeConfig("BlurMode", {blur_mode});
        d.writeConfig("BlurRadius", {blur_radius});
        d.writeConfig("BlurAnimationDuration", {blur_anim_duration});
        d.writeConfig("BlurOnOriginalProportions", {blur_on_original});
        d.writeConfig("BatterySaverEnabled", {battery_enabled});
        d.writeConfig("BatteryThreshold", {battery_threshold});
        d.writeConfig("CheckWindowsFromAllScreens", {check_all_screens});
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
