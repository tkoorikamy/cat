import os
from pathlib import Path


APP_SHORTCUT_NAME = "CatCompanion.lnk"


def _startup_folder() -> Path:
    appdata = os.getenv("APPDATA", "")
    return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def _shortcut_path() -> Path:
    return _startup_folder() / APP_SHORTCUT_NAME


def is_enabled() -> bool:
    return _shortcut_path().exists()


def enable(exe_path: str) -> None:
    import win32com.client  # type: ignore

    startup = _startup_folder()
    startup.mkdir(parents=True, exist_ok=True)
    shortcut = win32com.client.Dispatch("WScript.Shell").CreateShortcut(str(_shortcut_path()))
    shortcut.TargetPath = exe_path
    shortcut.WorkingDirectory = str(Path(exe_path).parent)
    shortcut.IconLocation = exe_path
    shortcut.Save()


def disable() -> None:
    sp = _shortcut_path()
    if sp.exists():
        sp.unlink()
