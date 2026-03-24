"""Wallpaper library grid view with preview panel and per-screen selector."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QSize, Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
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

from livepaper.models import MonitorMode, WallpaperEntry
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
    thumbnail_ready = pyqtSignal(int, Path)

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
    GRID_COLUMNS = 4

    def __init__(self, service: WallpaperService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._service = service
        self._cards: list[WallpaperCard] = []
        self._selected_entry: WallpaperEntry | None = None
        self._setup_ui()
        self._load_wallpapers()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(12)

        page_title = QLabel("Wallpapers")
        page_title.setStyleSheet("font-size: 22px; font-weight: bold;")
        toolbar.addWidget(page_title)
        toolbar.addStretch(1)

        self._add_btn = QPushButton("＋  Add wallpaper")
        self._add_btn.setFixedHeight(36)
        self._add_btn.setStyleSheet("""
            QPushButton {
                border-radius: 8px; padding: 8px 20px; font-size: 13px; font-weight: bold;
                background-color: #228be6; color: #ffffff; border: none;
            }
            QPushButton:hover { background-color: #339af0; }
        """)
        self._add_btn.clicked.connect(self.open_add_dialog)
        toolbar.addWidget(self._add_btn)
        layout.addLayout(toolbar)

        # Main content — grid + preview
        content = QHBoxLayout()
        content.setSpacing(16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._grid_container = QWidget()
        self._grid_layout = QGridLayout(self._grid_container)
        self._grid_layout.setSpacing(16)
        self._grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll.setWidget(self._grid_container)
        content.addWidget(scroll, 3)

        self._preview_panel = self._build_preview_panel()
        self._preview_panel.setVisible(False)
        content.addWidget(self._preview_panel, 1)
        layout.addLayout(content, 1)

        self._empty_label = QLabel(
            "No wallpapers yet.\nClick '＋ Add wallpaper' to get started."
        )
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet("font-size: 16px; color: palette(mid); padding: 60px;")
        layout.addWidget(self._empty_label)

    def _build_preview_panel(self) -> QFrame:
        panel = QFrame()
        panel.setFixedWidth(270)
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        panel.setStyleSheet("QFrame { border-radius: 12px; }")

        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        self._preview_title = QLabel()
        self._preview_title.setStyleSheet("font-size: 15px; font-weight: bold;")
        self._preview_title.setWordWrap(True)
        layout.addWidget(self._preview_title)

        self._preview_thumb = QLabel()
        self._preview_thumb.setFixedHeight(145)
        self._preview_thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_thumb.setStyleSheet("border-radius: 8px; background: palette(base);")
        layout.addWidget(self._preview_thumb)

        self._preview_path = QLabel()
        self._preview_path.setStyleSheet("font-size: 11px; color: palette(mid);")
        self._preview_path.setWordWrap(True)
        layout.addWidget(self._preview_path)

        layout.addSpacing(4)

        # Screen selector (shown when monitor_mode = per_screen)
        screen_row = QHBoxLayout()
        screen_row.setSpacing(6)
        screen_label = QLabel("Screen:")
        screen_label.setStyleSheet("font-size: 12px;")
        screen_row.addWidget(screen_label)
        self._screen_combo = QComboBox()
        self._screen_combo.addItem("All screens", -1)
        # Screens 0-3 (we add statically; could be dynamic via xrandr later)
        for i in range(4):
            self._screen_combo.addItem(f"Screen {i}", i)
        self._screen_combo.setFixedWidth(120)
        screen_row.addWidget(self._screen_combo)
        screen_row.addStretch()
        layout.addLayout(screen_row)

        # Apply buttons
        apply_desktop_btn = self._action_btn(
            "🖥  Apply to desktop", "#228be6", "#339af0"
        )
        apply_desktop_btn.clicked.connect(lambda: self._apply_selected(WallpaperTarget.DESKTOP))
        layout.addWidget(apply_desktop_btn)

        apply_lock_btn = self._action_btn(
            "🔒  Apply to lock screen", "#7048e8", "#845ef7"
        )
        apply_lock_btn.clicked.connect(lambda: self._apply_selected(WallpaperTarget.LOCK_SCREEN))
        layout.addWidget(apply_lock_btn)

        apply_both_btn = self._action_btn(
            "✨  Apply to both", "#0c8599", "#15aabf"
        )
        apply_both_btn.clicked.connect(lambda: self._apply_selected(WallpaperTarget.BOTH))
        layout.addWidget(apply_both_btn)

        layout.addStretch(1)

        remove_btn = QPushButton("Remove from library")
        remove_btn.setStyleSheet("""
            QPushButton {
                border-radius: 8px; padding: 8px 16px; font-size: 12px;
                background-color: rgba(255,59,48,0.12); color: #ff6b6b;
                border: 1px solid rgba(255,59,48,0.3);
            }
            QPushButton:hover { background-color: rgba(255,59,48,0.22); }
        """)
        remove_btn.clicked.connect(self._remove_selected)
        layout.addWidget(remove_btn)

        return panel

    def _action_btn(self, text: str, bg: str, bg_hover: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                border-radius: 8px; padding: 10px 14px; font-size: 13px;
                background-color: {bg}; color: #ffffff; border: none;
            }}
            QPushButton:hover {{ background-color: {bg_hover}; }}
        """)
        return btn

    # ------------------------------------------------------------------

    def _load_wallpapers(self) -> None:
        for card in self._cards:
            card.setParent(None)
            card.deleteLater()
        self._cards.clear()

        config = self._service.reload_config()

        # Update screen selector visibility
        is_per_screen = config.monitor_mode == MonitorMode.PER_SCREEN
        self._screen_combo.parentWidget().setVisible(False)  # hidden until a card is selected
        _ = is_per_screen  # used when card is selected

        wallpapers = config.wallpapers
        has = bool(wallpapers)
        self._empty_label.setVisible(not has)
        self._grid_container.setVisible(has)

        if not has:
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
            self._grid_layout.addWidget(card, i // self.GRID_COLUMNS, i % self.GRID_COLUMNS)

        self._thumb_worker = _ThumbnailWorker(wallpapers)
        self._thumb_worker.thumbnail_ready.connect(self._on_thumbnail_ready)
        self._thumb_worker.start()

    def _on_thumbnail_ready(self, index: int, thumb_path: Path) -> None:
        if 0 <= index < len(self._cards):
            self._cards[index].update_thumbnail(thumb_path)

    def _on_card_clicked(self, entry: WallpaperEntry) -> None:
        self._selected_entry = entry
        for card in self._cards:
            card.set_selected(card.entry.path == entry.path)

        self._preview_title.setText(entry.name)
        self._preview_path.setText(str(entry.path))

        if entry.thumbnail_path and entry.thumbnail_path.exists():
            from PyQt6.QtGui import QPixmap
            pixmap = QPixmap(str(entry.thumbnail_path))
            scaled = pixmap.scaled(
                QSize(250, 140),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._preview_thumb.setPixmap(scaled)
        else:
            self._preview_thumb.setText("🎬")
            self._preview_thumb.setStyleSheet("font-size: 42px; background: palette(base);")

        # Show screen selector only in per-screen mode
        cfg = self._service.config
        screen_row_widget = self._screen_combo.parent()
        if screen_row_widget:
            screen_row_widget.setVisible(cfg.monitor_mode == MonitorMode.PER_SCREEN)

        self._preview_panel.setVisible(True)

    def _apply_selected(self, target: WallpaperTarget) -> None:
        if self._selected_entry:
            self._apply_entry(self._selected_entry, target)

    def _apply_entry(self, entry: WallpaperEntry, target: WallpaperTarget) -> None:
        screen_index = self._screen_combo.currentData()
        try:
            self._service.apply_wallpaper([entry.path], target=target, screen_index=screen_index)
            target_label = target.value
            QMessageBox.information(self, "Applied", f"Wallpaper applied to {target_label}.")
        except FileNotFoundError as e:
            QMessageBox.critical(self, "File not found", str(e))
        except DBusError as e:
            QMessageBox.critical(
                self,
                "DBus error",
                f"{e}\n\nMake sure plasmashell is running and kde-cli-tools is installed.",
            )

    def _remove_selected(self) -> None:
        if self._selected_entry:
            self._on_remove_requested(self._selected_entry)

    def _on_remove_requested(self, entry: WallpaperEntry) -> None:
        reply = QMessageBox.question(
            self,
            "Remove wallpaper",
            f"Remove '{entry.name}' from the library?\n(The file will not be deleted.)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            remove_wallpaper_from_library(entry.path)
            self._selected_entry = None
            self._preview_panel.setVisible(False)
            self._load_wallpapers()

    def open_add_dialog(self) -> None:
        paths = open_add_wallpaper_dialog(self)
        if paths:
            add_wallpapers_to_library(paths)
            self._load_wallpapers()
