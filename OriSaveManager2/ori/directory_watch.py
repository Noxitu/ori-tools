import ctypes


WAIT_OBJECT_0 = 0x000
WAIT_OBJECT_1 = 0x001
WAIT_TIMEOUT = 0x102

FILE_NOTIFY_CHANGE_FILE_NAME = 0x001
FILE_NOTIFY_CHANGE_LAST_WRITE = 0x010


WAIT_TIMEOUT_MS = 1000


def ctypes_handles(*args):
    return len(args), ctypes.byref((len(args) * ctypes.c_void_p)(*args))


class DirectoryWatch:
    def __init__(self, path, callback):
        self._loop = True
        self._path = path
        self._callback = callback

    def start(self):
        kernel32 = ctypes.windll.kernel32

        self._event = kernel32.CreateEventW(None, True, False, None)
        notification_handle = kernel32.FindFirstChangeNotificationW(
            self._path,
            False,
            FILE_NOTIFY_CHANGE_FILE_NAME | FILE_NOTIFY_CHANGE_LAST_WRITE
        )

        while self._loop:
            ret = kernel32.WaitForMultipleObjects(
                *ctypes_handles(self._event, notification_handle),
                False,
                WAIT_TIMEOUT_MS
            )

            if ret == WAIT_TIMEOUT:
                continue

            if ret == WAIT_OBJECT_0:
                break

            if ret == WAIT_OBJECT_1:
                kernel32.FindNextChangeNotification(notification_handle)
                self._callback()
                continue

            raise Exception(f'Unexpected return value from WaitForMultipleObjects: {ret}')         

        kernel32.FindCloseChangeNotification(notification_handle)
        kernel32.CloseHandle(self._event)
        self._event = None

    def stop(self):
        ctypes.windll.kernel32.SetEvent(self._event)
