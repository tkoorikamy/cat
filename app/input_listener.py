import threading
import time
from dataclasses import dataclass

from pynput import keyboard, mouse


@dataclass
class InputState:
    last_key_ts: float = 0.0
    last_mouse_ts: float = 0.0
    mouse_dx: float = 0.0


class InputListener:
    """Tracks only activity fact; never stores typed text or concrete keys."""

    def __init__(self) -> None:
        self.state = InputState()
        self._lock = threading.Lock()
        self._last_mouse_pos: tuple[int, int] | None = None
        self._kbd = keyboard.Listener(on_press=self._on_key_press)
        self._mouse = mouse.Listener(on_move=self._on_move)

    def start(self) -> None:
        self._kbd.start()
        self._mouse.start()

    def stop(self) -> None:
        self._kbd.stop()
        self._mouse.stop()

    def _on_key_press(self, _key) -> None:
        with self._lock:
            self.state.last_key_ts = time.time()

    def _on_move(self, x: int, y: int) -> None:
        with self._lock:
            now = time.time()
            if self._last_mouse_pos:
                dx = x - self._last_mouse_pos[0]
                self.state.mouse_dx = dx
            self._last_mouse_pos = (x, y)
            self.state.last_mouse_ts = now

    def snapshot(self) -> InputState:
        with self._lock:
            return InputState(
                last_key_ts=self.state.last_key_ts,
                last_mouse_ts=self.state.last_mouse_ts,
                mouse_dx=self.state.mouse_dx,
            )
