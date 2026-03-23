"""DBus client for KDE Plasma wallpaper control."""

from __future__ import annotations

import subprocess
from pathlib import Path


class DBusError(Exception):
    """Raised when a DBus command fails."""


def _sanitize_path(path: Path) -> str:
    """Sanitize a file path for safe use in JavaScript strings."""
    resolved = str(path.resolve())
    # Escape backslashes and quotes for JS string embedding
    return resolved.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"')


def _build_wallpaper_script(
    video_paths: list[Path],
    screen_index: int = 0,
) -> str:
    """Build the Plasma evaluateScript JS to set the video wallpaper plugin.

    This sets the wallpaper type to 'smart-video-wallpaper-reborn' and
    configures the VideoUrls property with the given video file paths.
    """
    # Build a comma-separated, properly escaped URL list
    sanitized_urls = [_sanitize_path(p) for p in video_paths]
    urls_value = ",".join(f"file://{u}" for u in sanitized_urls)

    # JavaScript for Plasma's evaluateScript API
    script = f"""
var allDesktops = desktops();
for (var i = 0; i < allDesktops.length; i++) {{
    var d = allDesktops[i];
    if (d.screen === {screen_index} || {screen_index} < 0) {{
        d.wallpaperPlugin = "smart-video-wallpaper-reborn";
        d.currentConfigGroup = Array("Wallpaper", "smart-video-wallpaper-reborn", "General");
        d.writeConfig("VideoUrls", "{urls_value}");
    }}
}}
""".strip()

    return script


def apply_desktop_wallpaper(
    video_paths: list[Path],
    screen_index: int = -1,
) -> None:
    """Apply video wallpaper(s) to the desktop via Plasma's DBus API.

    Args:
        video_paths: List of video file paths to set as wallpaper.
        screen_index: Screen to apply to (-1 = all screens).

    Raises:
        DBusError: If the qdbus command fails.
        FileNotFoundError: If any video file doesn't exist.
    """
    for p in video_paths:
        if not p.exists():
            msg = f"Video file not found: {p}"
            raise FileNotFoundError(msg)

    script = _build_wallpaper_script(video_paths, screen_index)

    cmd = [
        "qdbus",
        "org.kde.plasmashell",
        "/PlasmaShell",
        "org.kde.PlasmaShell.evaluateScript",
        script,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode != 0:
            msg = f"qdbus command failed: {result.stderr.strip()}"
            raise DBusError(msg)
    except FileNotFoundError:
        msg = "qdbus command not found. Is kde-cli-tools installed?"
        raise DBusError(msg) from None
    except subprocess.TimeoutExpired:
        msg = "qdbus command timed out"
        raise DBusError(msg) from None


def get_evaluate_script_command(
    video_paths: list[Path],
    screen_index: int = -1,
) -> list[str]:
    """Return the qdbus command that would be executed (for testing/preview).

    Args:
        video_paths: List of video file paths.
        screen_index: Screen to apply to (-1 = all).

    Returns:
        The command as a list of strings.
    """
    script = _build_wallpaper_script(video_paths, screen_index)
    return [
        "qdbus",
        "org.kde.plasmashell",
        "/PlasmaShell",
        "org.kde.PlasmaShell.evaluateScript",
        script,
    ]
