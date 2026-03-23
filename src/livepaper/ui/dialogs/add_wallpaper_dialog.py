"""Add wallpaper file picker dialog."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import QFileDialog, QWidget

VIDEO_EXTENSIONS = "Video Files (*.mp4 *.mkv *.webm *.avi *.mov *.wmv *.flv *.m4v)"
ALL_EXTENSIONS = "All Files (*)"


def open_add_wallpaper_dialog(parent: QWidget | None = None) -> list[Path]:
    """Open a native file dialog to select video files.

    Returns:
        List of selected Paths, or empty list if cancelled.
    """
    file_paths, _ = QFileDialog.getOpenFileNames(
        parent,
        "Add Video Wallpapers",
        str(Path.home()),
        f"{VIDEO_EXTENSIONS};;{ALL_EXTENSIONS}",
    )

    result: list[Path] = []
    for fp in file_paths:
        p = Path(fp)
        if p.exists() and p.is_file():
            result.append(p)

    return result
