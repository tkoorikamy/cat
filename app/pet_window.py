import random
import subprocess
import sys
import time
from pathlib import Path

from PySide6.QtCore import QTimer, Qt, QSize
from PySide6.QtGui import QAction, QCursor, QIcon, QPixmap, QTransform
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QMenu

from app import autostart
from app.input_listener import InputListener
from app.settings import AppSettings, SettingsStore
from app.tray import TrayController

ASSETS = [
    "cat_idle_0.png", "cat_idle_1.png", "cat_idle_2.png",
    "cat_typing_0.png", "cat_typing_1.png", "cat_typing_2.png",
    "cat_mouse_0.png", "cat_mouse_1.png", "cat_mouse_2.png",
    "cat_sleep_0.png", "cat_sleep_1.png", "tray_icon.png",
]


class PetWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.assets_dir = Path(__file__).resolve().parents[1] / "assets"
        self._ensure_assets()

        self.store = SettingsStore()
        self.settings = self.store.load()
        self.settings.autostart = autostart.is_enabled()

        self.state = "idle"
        self.listener = InputListener()
        self.listener.start()
        self.drag_start = None
        self.move_mode = False
        self.current_frame = 0

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.label = QLabel(self)
        self.setCentralWidget(self.label)

        self._set_size(self.settings.size)
        self._apply_corner_or_position()
        self.apply_click_through(self.settings.click_through)

        self.tray = TrayController(self, str(self.assets_dir / "tray_icon.png"))

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(120)

    def _ensure_assets(self) -> None:
        missing = [a for a in ASSETS if not (self.assets_dir / a).exists()]
        if missing:
            tools_script = Path(__file__).resolve().parents[1] / "tools" / "generate_assets.py"
            subprocess.run([sys.executable, str(tools_script)], check=True)

    def _set_size(self, size: str) -> None:
        dims = {"small": 164, "medium": 220, "large": 300}
        self.sprite_size = dims.get(size, 220)
        self.settings.size = size
        self.resize(QSize(self.sprite_size, self.sprite_size))

    def _apply_corner_or_position(self) -> None:
        geo = QApplication.primaryScreen().availableGeometry()
        w, h = self.width(), self.height()
        margin = 20
        if self.settings.x is not None and self.settings.y is not None:
            self.move(self.settings.x, self.settings.y)
            return
        if self.settings.corner == "bottom-right":
            self.move(geo.right() - w - margin, geo.bottom() - h - margin)
        elif self.settings.corner == "bottom-left":
            self.move(geo.left() + margin, geo.bottom() - h - margin)
        elif self.settings.corner == "top-right":
            self.move(geo.right() - w - margin, geo.top() + margin)
        else:
            self.move(geo.left() + margin, geo.top() + margin)

    def set_corner(self, corner: str) -> None:
        self.settings.corner = corner
        self.settings.x = None
        self.settings.y = None
        self._apply_corner_or_position()
        self._save()

    def set_size(self, size: str) -> None:
        self._set_size(size)
        self._apply_corner_or_position()
        self._save()

    def toggle_pause(self) -> None:
        self.settings.paused = not self.settings.paused
        self.tray.set_paused(self.settings.paused)
        self._save()

    def toggle_click_through(self) -> None:
        self.settings.click_through = not self.settings.click_through
        self.apply_click_through(self.settings.click_through)
        self._save()

    def toggle_autostart(self) -> None:
        if autostart.is_enabled():
            autostart.disable()
            self.settings.autostart = False
        else:
            exe_path = sys.executable if getattr(sys, "frozen", False) else str(Path(sys.argv[0]).resolve())
            autostart.enable(exe_path)
            self.settings.autostart = True
        self._save()

    def apply_click_through(self, enabled: bool) -> None:
        self.setAttribute(Qt.WA_TransparentForMouseEvents, enabled and not self.move_mode)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        move = QAction("Toggle move mode", self)
        move.triggered.connect(self.toggle_move_mode)
        menu.addAction(move)
        menu.addAction("Exit", self.exit_app)
        menu.exec(QCursor.pos())

    def toggle_move_mode(self):
        self.move_mode = not self.move_mode
        self.apply_click_through(self.settings.click_through)

    def mousePressEvent(self, event):
        if event.modifiers() & Qt.ShiftModifier or self.move_mode:
            self.drag_start = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_start is not None:
            self.move(event.globalPosition().toPoint() - self.drag_start)
            event.accept()

    def mouseReleaseEvent(self, _event):
        self.drag_start = None
        self.settings.x, self.settings.y = self.x(), self.y()
        self._save()

    def tick(self):
        if self.settings.paused:
            self._render("idle")
            return
        snap = self.listener.snapshot()
        now = time.time()
        if now - max(snap.last_key_ts, snap.last_mouse_ts) > 45:
            desired = "sleep"
        elif now - snap.last_key_ts < 1.5:
            desired = "typing"
        elif now - snap.last_mouse_ts < 0.6:
            desired = "mouse"
        else:
            desired = "idle"

        if desired == "mouse" and random.random() < 0.25:
            desired = "mouse"
        self._render(desired, snap.mouse_dx)

    def _render(self, state: str, mouse_dx: float = 0.0):
        self.state = state
        frames = {
            "idle": ["cat_idle_0.png", "cat_idle_1.png", "cat_idle_2.png"],
            "typing": ["cat_typing_0.png", "cat_typing_1.png", "cat_typing_2.png"],
            "mouse": ["cat_mouse_0.png", "cat_mouse_1.png", "cat_mouse_2.png"],
            "sleep": ["cat_sleep_0.png", "cat_sleep_1.png"],
        }[state]
        self.current_frame = (self.current_frame + 1) % len(frames)
        pix = QPixmap(str(self.assets_dir / frames[self.current_frame]))
        if state == "mouse" and mouse_dx < -3:
            pix = pix.transformed(QTransform().scale(-1, 1))
        self.label.setPixmap(pix.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def exit_app(self):
        self.listener.stop()
        self._save()
        QApplication.quit()

    def _save(self):
        self.store.save(self.settings)


def run():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    w = PetWindow()
    w.show()
    sys.exit(app.exec())
