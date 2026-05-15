from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon


class TrayController:
    def __init__(self, parent, icon_path: str):
        self.parent = parent
        self.tray = QSystemTrayIcon(QIcon(icon_path), parent)
        self.menu = QMenu()
        self.pause_action = QAction("Pause", parent)
        self.pause_action.triggered.connect(parent.toggle_pause)
        self.menu.addAction(self.pause_action)

        corner_menu = self.menu.addMenu("Change corner")
        for c in ["bottom-right", "bottom-left", "top-right", "top-left"]:
            act = QAction(c, parent)
            act.triggered.connect(lambda _=False, cc=c: parent.set_corner(cc))
            corner_menu.addAction(act)

        size_menu = self.menu.addMenu("Size")
        for s in ["small", "medium", "large"]:
            act = QAction(s, parent)
            act.triggered.connect(lambda _=False, ss=s: parent.set_size(ss))
            size_menu.addAction(act)

        click_action = QAction("Toggle click-through", parent)
        click_action.triggered.connect(parent.toggle_click_through)
        self.menu.addAction(click_action)

        auto_action = QAction("Toggle autostart", parent)
        auto_action.triggered.connect(parent.toggle_autostart)
        self.menu.addAction(auto_action)

        exit_action = QAction("Exit", parent)
        exit_action.triggered.connect(parent.exit_app)
        self.menu.addAction(exit_action)

        self.tray.setContextMenu(self.menu)
        self.tray.show()

    def set_paused(self, paused: bool) -> None:
        self.pause_action.setText("Resume" if paused else "Pause")
