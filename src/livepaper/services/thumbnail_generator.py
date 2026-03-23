"""Thumbnail generator for video files using ffmpeg."""

from __future__ import annotations

import hashlib
import subprocess  # nosec B404
from pathlib import Path

CACHE_DIR = Path.home() / ".cache" / "livepaper" / "thumbnails"


def _get_cache_path(video_path: Path, cache_dir: Path | None = None) -> Path:
    """Generate a deterministic cache path for a video's thumbnail."""
    target_dir = cache_dir or CACHE_DIR
    # Use hash of absolute path for unique, safe filenames
    path_hash = hashlib.sha256(str(video_path.resolve()).encode()).hexdigest()[:16]
    return target_dir / f"{path_hash}.jpg"


def generate_thumbnail(
    video_path: Path,
    cache_dir: Path | None = None,
    timestamp: str = "00:00:01",
    size: str = "320x180",
) -> Path | None:
    """Extract a thumbnail frame from a video using ffmpeg.

    Args:
        video_path: Path to the video file.
        cache_dir: Optional override for the cache directory.
        timestamp: Time position to extract the frame from.
        size: Output resolution (WxH).

    Returns:
        Path to the generated thumbnail, or None on failure.
    """
    if not video_path.exists():
        return None

    target_dir = cache_dir or CACHE_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    output_path = _get_cache_path(video_path, target_dir)

    # Return cached thumbnail if it exists and is newer than the video
    if output_path.exists() and output_path.stat().st_mtime >= video_path.stat().st_mtime:
        return output_path

    cmd = [
        "ffmpeg",
        "-y",  # Overwrite output
        "-ss",
        timestamp,  # Seek position
        "-i",
        str(video_path.resolve()),
        "-vframes",
        "1",  # Extract one frame
        "-s",
        size,  # Output size
        "-q:v",
        "3",  # JPEG quality (2-5 is good)
        str(output_path),
    ]

    try:
        result = subprocess.run(  # nosec B603
            cmd,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
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
