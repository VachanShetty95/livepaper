"""Thumbnail generator for video files using ffmpeg."""

from __future__ import annotations

import hashlib
import subprocess  # nosec B404
from pathlib import Path

CACHE_DIR = Path.home() / ".cache" / "livepaper" / "thumbnails"


def _get_cache_path(video_path: Path, cache_dir: Path | None = None) -> Path:
    target_dir = cache_dir or CACHE_DIR
    path_hash = hashlib.sha256(str(video_path.resolve()).encode()).hexdigest()[:16]
    return target_dir / f"{path_hash}.jpg"


def generate_thumbnail(
    video_path: Path,
    cache_dir: Path | None = None,
    timestamp: str = "00:00:01",
    size: str = "320x180",
) -> Path | None:
    """Extract a thumbnail frame from a video using ffmpeg."""
    if not video_path.exists():
        return None

    target_dir = cache_dir or CACHE_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    output_path = _get_cache_path(video_path, target_dir)

    if output_path.exists() and output_path.stat().st_mtime >= video_path.stat().st_mtime:
        return output_path

    cmd = [
        "ffmpeg", "-y",
        "-ss", timestamp,
        "-i", str(video_path.resolve()),
        "-vframes", "1",
        "-s", size,
        "-q:v", "3",
        str(output_path),
    ]

    try:
        result = subprocess.run(  # nosec B603
            cmd, capture_output=True, text=True, timeout=15, check=False,
        )
        if result.returncode == 0 and output_path.exists():
            return output_path
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass

    return None


def clear_thumbnail_cache(cache_dir: Path | None = None) -> int:
    """Remove all cached thumbnails. Returns count of files removed."""
    target_dir = cache_dir or CACHE_DIR
    if not target_dir.exists():
        return 0
    count = 0
    for thumb in target_dir.glob("*.jpg"):
        thumb.unlink(missing_ok=True)
        count += 1
    return count
