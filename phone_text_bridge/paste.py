"""Paste text into the active desktop text field."""

from __future__ import annotations

from dataclasses import dataclass
import ctypes
from ctypes import wintypes
import time

import pyperclip
from pynput.keyboard import Controller, Key


@dataclass(frozen=True)
class PasteResult:
    attempted: bool
    verified_target: bool


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]


class GUITHREADINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("hwndActive", wintypes.HWND),
        ("hwndFocus", wintypes.HWND),
        ("hwndCapture", wintypes.HWND),
        ("hwndMenuOwner", wintypes.HWND),
        ("hwndMoveSize", wintypes.HWND),
        ("hwndCaret", wintypes.HWND),
        ("rcCaret", RECT),
    ]


user32 = ctypes.WinDLL("user32", use_last_error=True)
user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.GetGUIThreadInfo.argtypes = [wintypes.DWORD, ctypes.POINTER(GUITHREADINFO)]
user32.GetGUIThreadInfo.restype = wintypes.BOOL


def active_text_field_available() -> bool:
    """Return True when Windows reports a visible caret in the active window."""
    foreground = user32.GetForegroundWindow()
    if not foreground:
        return False

    process_id = wintypes.DWORD()
    thread_id = user32.GetWindowThreadProcessId(foreground, ctypes.byref(process_id))
    if not thread_id:
        return False

    info = GUITHREADINFO()
    info.cbSize = ctypes.sizeof(GUITHREADINFO)
    if not user32.GetGUIThreadInfo(thread_id, ctypes.byref(info)):
        return False

    return bool(info.hwndCaret)


def paste_text(text: str) -> PasteResult:
    cleaned = text.strip()
    if not cleaned:
        return PasteResult(attempted=False, verified_target=False)

    verified_target = active_text_field_available()
    keyboard = Controller()
    previous = pyperclip.paste()
    pyperclip.copy(cleaned)
    time.sleep(0.05)
    with keyboard.pressed(Key.ctrl):
        keyboard.press("v")
        keyboard.release("v")
    time.sleep(0.1)
    pyperclip.copy(previous)
    return PasteResult(attempted=True, verified_target=verified_target)
