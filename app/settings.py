import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path

APP_NAME = "CatCompanion"


def _settings_path() -> Path:
    base = os.getenv("APPDATA")
    if base:
        folder = Path(base) / APP_NAME
    else:
        folder = Path(__file__).resolve().parents[1]
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "settings.json"


@dataclass
class AppSettings:
    corner: str = "bottom-right"
    size: str = "medium"
    click_through: bool = True
    autostart: bool = False
    paused: bool = False
    x: int | None = None
    y: int | None = None


class SettingsStore:
    def __init__(self) -> None:
        self.path = _settings_path()

    def load(self) -> AppSettings:
        if not self.path.exists():
            return AppSettings()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return AppSettings(**data)
        except Exception:
            return AppSettings()

    def save(self, settings: AppSettings) -> None:
        self.path.write_text(json.dumps(asdict(settings), ensure_ascii=False, indent=2), encoding="utf-8")
