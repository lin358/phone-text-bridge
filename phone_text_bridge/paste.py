"""Paste text into the active desktop field."""

from __future__ import annotations

import time

import pyperclip
from pynput.keyboard import Controller, Key


def paste_text(text: str) -> None:
    cleaned = text.strip()
    if not cleaned:
        return

    keyboard = Controller()
    previous = pyperclip.paste()
    pyperclip.copy(cleaned)
    time.sleep(0.05)
    with keyboard.pressed(Key.ctrl):
        keyboard.press("v")
        keyboard.release("v")
    time.sleep(0.1)
    pyperclip.copy(previous)

