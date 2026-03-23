"""Shared UI utility functions."""

from __future__ import annotations


def open_url(url: str) -> None:
    """Open a URL in the system's default browser."""
    from PyQt6.QtCore import QUrl
    from PyQt6.QtGui import QDesktopServices

    QDesktopServices.openUrl(QUrl(url))
