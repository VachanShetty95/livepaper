"""System detection utilities for KDE Plasma environment."""

from __future__ import annotations

import shutil
import subprocess  # nosec B404
from pathlib import Path

from livepaper.models import SystemStatus


def _run_command(cmd: list[str], timeout: int = 5) -> str | None:
    """Run a command and return stdout, or None on failure."""
    try:
        result = subprocess.run(  # nosec B603
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None


def detect_plasma_version() -> tuple[bool, str]:
    """Detect KDE Plasma version. Returns (is_plasma6, version_string)."""
    output = _run_command(["plasmashell", "--version"])
    if output is None:
        return False, ""

    for line in output.splitlines():
        parts = line.strip().split()
        if len(parts) >= 2:
            version_str = parts[-1]
            try:
                major = int(version_str.split(".")[0])
                return major >= 6, version_str
            except (ValueError, IndexError):
                continue
    return False, ""


def detect_plugin_installed() -> bool:
    """Check if the Smart Video Wallpaper Reborn plugin is installed."""
    for pkg in [
        "plasma6-wallpapers-smart-video-wallpaper-reborn",
        "plasma6-wallpapers-smart-video-wallpaper-reborn-git",
    ]:
        if _run_command(["pacman", "-Qi", pkg]) is not None:
            return True

    plugin_dirs = [
        Path.home() / ".local/share/plasma/wallpapers",
        Path("/usr/share/plasma/wallpapers"),
    ]
    plugin_patterns = [
        "*smart*video*wallpaper*reborn*",
        "luisbocanegra.smart.video.wallpaper.reborn",
    ]
    for base_dir in plugin_dirs:
        if base_dir.exists():
            for pattern in plugin_patterns:
                if list(base_dir.glob(pattern)):
                    return True
    return False


def detect_codecs_available() -> bool:
    """Check if required multimedia codecs are available."""
    result = _run_command(["pacman", "-Qi", "qt6-multimedia-ffmpeg"])
    if result is not None:
        return True
    return shutil.which("ffmpeg") is not None


def detect_system_status() -> SystemStatus:
    """Run all system checks and return a status report."""
    plasma_ok, plasma_version = detect_plasma_version()
    plugin_installed = detect_plugin_installed()
    codecs_available = detect_codecs_available()

    return SystemStatus(
        plasma_version=plasma_version,
        plasma_ok=plasma_ok,
        plugin_installed=plugin_installed,
        codecs_available=codecs_available,
    )
