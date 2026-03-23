"""Main application window with sidebar navigation."""

from __future__ import annotations

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from livepaper.services.wallpaper_service import WallpaperService
from livepaper.ui.pages.about_page import AboutPage
from livepaper.ui.pages.library_view import LibraryView
from livepaper.ui.pages.settings_page import SettingsPage
from livepaper.ui.pages.setup_wizard import SetupWizardPage


class MainWindow(QMainWindow):
    """Primary application window with sidebar navigation."""

    NAV_ITEMS = [
        ("🏠  Home", "home"),
        ("🖼  Wallpapers", "wallpapers"),
        ("⚙  Settings", "settings"),
        ("ℹ  About", "about"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._service = WallpaperService()
        self._setup_window()
        self._setup_ui()
        self._setup_shortcuts()
        self._navigate_to_initial_page()

    def _setup_window(self) -> None:
        """Configure the main window properties."""
        self.setWindowTitle("Livepaper")
        self.setMinimumSize(900, 600)
        self.resize(1100, 700)

    def _setup_ui(self) -> None:
        """Build the sidebar + stacked content layout."""
        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- Sidebar ---
        self._sidebar = QListWidget()
        self._sidebar.setFixedWidth(200)
        self._sidebar.setIconSize(QSize(20, 20))
        self._sidebar.setSpacing(4)
        self._sidebar.setFrameShape(QListWidget.Shape.NoFrame)
        self._sidebar.setStyleSheet("""
            QListWidget {
                padding: 12px 8px;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 12px 16px;
                border-radius: 8px;
                margin: 2px 4px;
            }
            QListWidget::item:selected {
                font-weight: bold;
            }
        """)

        for label, _key in self.NAV_ITEMS:
            item = QListWidgetItem(label)
            item.setSizeHint(QSize(180, 44))
            self._sidebar.addItem(item)

        self._sidebar.currentRowChanged.connect(self._on_nav_changed)
        layout.addWidget(self._sidebar)

        # --- Content Area ---
        self._pages = QStackedWidget()

        self._setup_wizard = SetupWizardPage(on_continue=self._on_wizard_continue)
        self._library_view = LibraryView(service=self._service)
        self._settings_page = SettingsPage(service=self._service)
        self._about_page = AboutPage()

        self._pages.addWidget(self._setup_wizard)  # index 0 = Home
        self._pages.addWidget(self._library_view)  # index 1 = Wallpapers
        self._pages.addWidget(self._settings_page)  # index 2 = Settings
        self._pages.addWidget(self._about_page)  # index 3 = About

        layout.addWidget(self._pages, 1)

    def _setup_shortcuts(self) -> None:
        """Register keyboard shortcuts."""
        add_action = QAction("Add Wallpaper", self)
        add_action.setShortcut(QKeySequence("Ctrl+N"))
        add_action.triggered.connect(self._on_add_shortcut)
        self.addAction(add_action)

    def _navigate_to_initial_page(self) -> None:
        """Show wizard on first run, otherwise go to library."""
        config = self._service.config
        if config.first_run_complete:
            self._sidebar.setCurrentRow(1)  # Wallpapers
        else:
            self._sidebar.setCurrentRow(0)  # Home (wizard)

    def _on_nav_changed(self, index: int) -> None:
        """Handle sidebar navigation clicks."""
        if 0 <= index < self._pages.count():
            self._pages.setCurrentIndex(index)

    def _on_wizard_continue(self) -> None:
        """Called when the setup wizard is completed."""
        config = self._service.config
        updated = config.model_copy(update={"first_run_complete": True})
        self._service.save_config(updated)
        self._sidebar.setCurrentRow(1)  # Navigate to Wallpapers

    def _on_add_shortcut(self) -> None:
        """Handle Ctrl+N shortcut to add wallpaper."""
        self._sidebar.setCurrentRow(1)  # Go to library
        self._library_view.open_add_dialog()
