import ctypes
from ctypes import wintypes
import threading
import time

byref = ctypes.byref
user32 = ctypes.windll.user32

VK_END = 0x23
VK_HOME = 0x24

WM_QUIT = 0x12
WM_HOTKEY = 786

class Hotkey:
    next_id = 1
    hotkeys = {}

    def __init__(self, key, modifiers=0):
        self.key = key
        self.modifiers = modifiers
        self.id = Hotkey.next_id
        Hotkey.next_id += 1

        Hotkey.hotkeys[self.id] = self

    def __call__(self, call):
        self.call = call
        return call

    @staticmethod
    def register(*a):
        for self in Hotkey.hotkeys.values():
            user32.RegisterHotKey(None, self.id, self.modifiers, self.key)

    @staticmethod
    def unregister(*a):
        for self in Hotkey.hotkeys.values():
            user32.UnregisterHotKey(None, self.id)

    @staticmethod
    def hotkey(id):
        hotkey = Hotkey.hotkeys.get(id, None)
        if hotkey is not None:
            hotkey.call()

class EventLoop:
    def __enter__(self, *a):
        self.thread = threading.Thread(target=self.main)
        self.thread.start()

    def main(self):
        try:
            Hotkey.register()

            msg = wintypes.MSG()
            while True:
                ret = user32.GetMessageA(byref(msg), None, 0, 0)
                if ret == -1 or ret == 0:
                    break

                if msg.message == WM_HOTKEY:
                    Hotkey.hotkey(msg.wParam)

                user32.TranslateMessage(byref(msg))
                user32.DispatchMessageA(byref(msg))

        finally:
            Hotkey.unregister()

    def __exit__(self, *a):
        user32.PostThreadMessageA(self.thread.ident, WM_QUIT, 0, 0)
        self.thread.join()