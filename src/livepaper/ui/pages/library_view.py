"""Wallpaper library grid view with preview panel."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QSize, Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from livepaper.models import WallpaperEntry
from livepaper.services.config_manager import (
    add_wallpapers_to_library,
    remove_wallpaper_from_library,
)
from livepaper.services.dbus_client import DBusError
from livepaper.services.thumbnail_generator import generate_thumbnail
from livepaper.services.wallpaper_service import WallpaperService, WallpaperTarget
from livepaper.ui.dialogs.add_wallpaper_dialog import open_add_wallpaper_dialog
from livepaper.ui.widgets.wallpaper_card import WallpaperCard


class _ThumbnailWorker(QThread):
    """Generate thumbnails in a background thread."""

    thumbnail_ready = pyqtSignal(int, Path)  # (index, thumbnail_path)

    def __init__(self, entries: list[WallpaperEntry]) -> None:
        super().__init__()
        self._entries = entries

    def run(self) -> None:
        for i, entry in enumerate(self._entries):
            if entry.thumbnail_path and entry.thumbnail_path.exists():
                continue
            result = generate_thumbnail(entry.path)
            if result:
                self.thumbnail_ready.emit(i, result)


class LibraryView(QWidget):
    """Main wallpaper library with grid of cards and preview panel."""

    GRID_COLUMNS = 4

    def __init__(
        self,
        service: WallpaperService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._service = service
        self._cards: list[WallpaperCard] = []
        self._selected_entry: WallpaperEntry | None = None
        self._setup_ui()
        self._load_wallpapers()

    def _setup_ui(self) -> None:
        """Build the library layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # --- Toolbar ---
        toolbar = QHBoxLayout()
        toolbar.setSpacing(12)

        page_title = QLabel("Wallpapers")
        page_title.setStyleSheet("font-size: 22px; font-weight: bold;")
        toolbar.addWidget(page_title)

        toolbar.addStretch(1)

        self._add_btn = QPushButton("＋  Add Wallpaper")
        self._add_btn.setFixedHeight(36)
        self._add_btn.setStyleSheet("""
            QPushButton {
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: bold;
                background-color: #228be6;
                color: #ffffff;
                border: none;
            }
            QPushButton:hover {
                background-color: #339af0;
            }
        """)
        self._add_btn.clicked.connect(self.open_add_dialog)
        toolbar.addWidget(self._add_btn)

        layout.addLayout(toolbar)

        # --- Content (Grid + Preview) ---
        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)

        # Scroll area for grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._grid_container = QWidget()
        self._grid_layout = QGridLayout(self._grid_container)
        self._grid_layout.setSpacing(16)
        self._grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll.setWidget(self._grid_container)

        content_layout.addWidget(scroll, 3)

        # Preview panel
        self._preview_panel = self._build_preview_panel()
        self._preview_panel.setVisible(False)
        content_layout.addWidget(self._preview_panel, 1)

        layout.addLayout(content_layout, 1)

        # Empty state
        self._empty_label = QLabel("No wallpapers yet.\nClick 'Add Wallpaper' to get started.")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet("font-size: 16px; opacity: 0.5; padding: 60px;")
        layout.addWidget(self._empty_label)

    def _build_preview_panel(self) -> QFrame:
        """Build the side preview panel."""
        panel = QFrame()
        panel.setFixedWidth(260)
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        panel.setStyleSheet("""
            QFrame {
                border-radius: 12px;
                padding: 16px;
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setSpacing(12)

        self._preview_title = QLabel()
        self._preview_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self._preview_title.setWordWrap(True)
        layout.addWidget(self._preview_title)

        self._preview_thumb = QLabel()
        self._preview_thumb.setFixedHeight(140)
        self._preview_thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_thumb.setStyleSheet("border-radius: 8px;")
        layout.addWidget(self._preview_thumb)

        self._preview_path = QLabel()
        self._preview_path.setStyleSheet("font-size: 11px; opacity: 0.6;")
        self._preview_path.setWordWrap(True)
        layout.addWidget(self._preview_path)

        layout.addSpacing(8)

        # Action buttons
        apply_desktop_btn = QPushButton("🖥  Apply to Desktop")
        apply_desktop_btn.setStyleSheet("""
            QPushButton {
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 13px;
                background-color: #228be6;
                color: #ffffff;
                border: none;
            }
            QPushButton:hover {
                background-color: #339af0;
            }
        """)
        apply_desktop_btn.clicked.connect(lambda: self._apply_selected(WallpaperTarget.DESKTOP))
        layout.addWidget(apply_desktop_btn)

        apply_lock_btn = QPushButton("🔒  Apply to Lock Screen")
        apply_lock_btn.setStyleSheet("""
            QPushButton {
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 13px;
                background-color: #7048e8;
                color: #ffffff;
                border: none;
            }
            QPushButton:hover {
                background-color: #845ef7;
            }
        """)
        apply_lock_btn.clicked.connect(lambda: self._apply_selected(WallpaperTarget.LOCK_SCREEN))
        layout.addWidget(apply_lock_btn)

        apply_both_btn = QPushButton("✨  Apply to Both")
        apply_both_btn.setStyleSheet("""
            QPushButton {
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 13px;
                font-weight: bold;
                background-color: #1098ad;
                color: #ffffff;
                border: none;
            }
            QPushButton:hover {
                background-color: #15aabf;
            }
        """)
        apply_both_btn.clicked.connect(lambda: self._apply_selected(WallpaperTarget.BOTH))
        layout.addWidget(apply_both_btn)

        layout.addStretch(1)

        remove_btn = QPushButton("Remove")
        remove_btn.setStyleSheet("""
            QPushButton {
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 12px;
                background-color: rgba(255, 59, 48, 0.15);
                color: #ff6b6b;
                border: 1px solid rgba(255, 59, 48, 0.3);
            }
            QPushButton:hover {
                background-color: rgba(255, 59, 48, 0.25);
            }
        """)
        remove_btn.clicked.connect(self._remove_selected)
        layout.addWidget(remove_btn)

        return panel

    def _load_wallpapers(self) -> None:
        """Load wallpapers from config and populate the grid."""
        # Clear existing cards
        for card in self._cards:
            card.setParent(None)
            card.deleteLater()
        self._cards.clear()

        config = self._service.reload_config()
        wallpapers = config.wallpapers

        has_wallpapers = len(wallpapers) > 0
        self._empty_label.setVisible(not has_wallpapers)
        self._grid_container.setVisible(has_wallpapers)

        if not has_wallpapers:
            self._preview_panel.setVisible(False)
            return

        for i, entry in enumerate(wallpapers):
            card = WallpaperCard(entry)
            card.clicked.connect(self._on_card_clicked)
            card.remove_requested.connect(self._on_remove_requested)
            card.apply_desktop_requested.connect(
                lambda e: self._apply_entry(e, WallpaperTarget.DESKTOP)
            )
            card.apply_lockscreen_requested.connect(
                lambda e: self._apply_entry(e, WallpaperTarget.LOCK_SCREEN)
            )
            self._cards.append(card)

            row = i // self.GRID_COLUMNS
            col = i % self.GRID_COLUMNS
            self._grid_layout.addWidget(card, row, col)

        # Generate thumbnails in background
        self._thumb_worker = _ThumbnailWorker(wallpapers)
        self._thumb_worker.thumbnail_ready.connect(self._on_thumbnail_ready)
        self._thumb_worker.start()

    def _on_thumbnail_ready(self, index: int, thumb_path: Path) -> None:
        """Update a card's thumbnail when background generation completes."""
        if 0 <= index < len(self._cards):
            self._cards[index].update_thumbnail(thumb_path)

    def _on_card_clicked(self, entry: WallpaperEntry) -> None:
        """Handle card click — show preview panel."""
        self._selected_entry = entry

        # Update selection state
        for card in self._cards:
            card.set_selected(card.entry.path == entry.path)

        # Update preview panel
        self._preview_title.setText(entry.name)
        self._preview_path.setText(str(entry.path))

        if entry.thumbnail_path and entry.thumbnail_path.exists():
            from PyQt6.QtGui import QPixmap

            pixmap = QPixmap(str(entry.thumbnail_path))
            scaled = pixmap.scaled(
                QSize(240, 135),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._preview_thumb.setPixmap(scaled)
        else:
            self._preview_thumb.setText("🎬")
            self._preview_thumb.setStyleSheet("font-size: 48px;")

        self._preview_panel.setVisible(True)

    def _apply_selected(self, target: WallpaperTarget) -> None:
        """Apply the currently selected wallpaper."""
        if self._selected_entry:
            self._apply_entry(self._selected_entry, target)

    def _apply_entry(self, entry: WallpaperEntry, target: WallpaperTarget) -> None:
        """Apply a wallpaper entry to the specified target."""
        try:
            self._service.apply_wallpaper([entry.path], target)
            QMessageBox.information(
                self,
                "Success",
                f"Wallpaper applied to {target.value.replace('_', ' ')}!",
            )
        except (FileNotFoundError, DBusError) as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to apply wallpaper:\n{e}",
            )

    def _remove_selected(self) -> None:
        """Remove the selected wallpaper from the library."""
        if self._selected_entry:
            self._on_remove_requested(self._selected_entry)

    def _on_remove_requested(self, entry: WallpaperEntry) -> None:
        """Handle removal of a wallpaper from the library."""
        reply = QMessageBox.question(
            self,
            "Remove Wallpaper",
            f"Remove '{entry.name}' from library?\n(The file will not be deleted.)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            remove_wallpaper_from_library(entry.path)
            self._selected_entry = None
            self._preview_panel.setVisible(False)
            self._load_wallpapers()

    def open_add_dialog(self) -> None:
        """Open the add wallpaper file picker."""
        paths = open_add_wallpaper_dialog(self)
        if paths:
            add_wallpapers_to_library(paths)
            self._load_wallpapers()
