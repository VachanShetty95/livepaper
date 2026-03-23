"""Wallpaper card widget for the library grid."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QLabel,
    QMenu,
    QVBoxLayout,
    QWidget,
)

from livepaper.models import WallpaperEntry


class WallpaperCard(QFrame):
    """A single wallpaper card in the library grid.

    Displays a thumbnail, filename, and provides click/context-menu interactions.
    """

    CARD_WIDTH = 200
    CARD_HEIGHT = 160
    THUMB_HEIGHT = 120

    clicked = pyqtSignal(WallpaperEntry)
    remove_requested = pyqtSignal(WallpaperEntry)
    apply_desktop_requested = pyqtSignal(WallpaperEntry)
    apply_lockscreen_requested = pyqtSignal(WallpaperEntry)

    def __init__(
        self,
        entry: WallpaperEntry,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._entry = entry
        self._selected = False
        self._setup_ui()

    @property
    def entry(self) -> WallpaperEntry:
        """Return the wallpaper entry for this card."""
        return self._entry

    def _setup_ui(self) -> None:
        """Build the card layout."""
        self.setFixedSize(self.CARD_WIDTH, self.CARD_HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self._apply_style(selected=False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Thumbnail
        self._thumb_label = QLabel()
        self._thumb_label.setFixedHeight(self.THUMB_HEIGHT)
        self._thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._thumb_label.setStyleSheet("""
            QLabel {
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
        """)
        self._set_thumbnail()
        layout.addWidget(self._thumb_label)

        # Name label
        name_label = QLabel(self._entry.name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("""
            QLabel {
                padding: 8px 6px;
                font-size: 12px;
                font-weight: 500;
            }
        """)
        name_label.setWordWrap(False)
        layout.addWidget(name_label)

    def _set_thumbnail(self) -> None:
        """Load and display the thumbnail image."""
        if self._entry.thumbnail_path and self._entry.thumbnail_path.exists():
            pixmap = QPixmap(str(self._entry.thumbnail_path))
            scaled = pixmap.scaled(
                QSize(self.CARD_WIDTH, self.THUMB_HEIGHT),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._thumb_label.setPixmap(scaled)
        else:
            self._thumb_label.setText("🎬")
            self._thumb_label.setStyleSheet("""
                QLabel {
                    font-size: 36px;
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                }
            """)

    def _apply_style(self, *, selected: bool) -> None:
        """Apply visual style based on selection state."""
        border = "2px solid palette(highlight)" if selected else "1px solid palette(mid)"
        self.setStyleSheet(f"""
            WallpaperCard {{
                border: {border};
                border-radius: 10px;
            }}
            WallpaperCard:hover {{
                border: 2px solid palette(highlight);
            }}
        """)

    def set_selected(self, selected: bool) -> None:
        """Toggle the selected visual state."""
        self._selected = selected
        self._apply_style(selected=selected)

    def mousePressEvent(self, event: object) -> None:
        """Emit clicked signal on left click."""
        self.clicked.emit(self._entry)
        super().mousePressEvent(event)  # type: ignore[arg-type]

    def contextMenuEvent(self, event: object) -> None:
        """Show right-click context menu."""
        menu = QMenu(self)

        apply_desktop = QAction("Apply to Desktop", self)
        apply_desktop.triggered.connect(
            lambda: self.apply_desktop_requested.emit(self._entry)
        )
        menu.addAction(apply_desktop)

        apply_lock = QAction("Apply to Lock Screen", self)
        apply_lock.triggered.connect(
            lambda: self.apply_lockscreen_requested.emit(self._entry)
        )
        menu.addAction(apply_lock)

        menu.addSeparator()

        remove_action = QAction("Remove from Library", self)
        remove_action.triggered.connect(
            lambda: self.remove_requested.emit(self._entry)
        )
        menu.addAction(remove_action)

        menu.exec(event.globalPos())  # type: ignore[attr-defined]

    def update_thumbnail(self, thumbnail_path: Path) -> None:
        """Update the card's thumbnail after background generation."""
        self._entry = self._entry.model_copy(
            update={"thumbnail_path": thumbnail_path}
        )
        self._set_thumbnail()
