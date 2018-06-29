import ctypes
import os
import time
import sys
from updatesave import ori_get_save_path
import hotkey
import shutil

SAVE_SLOT_ID = int(sys.argv[1])
BACKUP_DIRECTORY = sys.argv[2]
os.makedirs(BACKUP_DIRECTORY, exist_ok=True)

PATH = ori_get_save_path(SAVE_SLOT_ID)
ZERO_TIME = time.time()
last_modified = ZERO_TIME

def timediff2str(diff):
    format = '{m:02d}:{s:02d}.{s10:01d}'
    if diff >= 3600:
        format = '{h:d}:' + format

    diff_high = int(diff//1)
    diff_low = diff%1
    return format.format(h=diff_high//3600, m=diff_high//60%60, s=diff_high%60, s10=int(diff_low*10))

@hotkey.Hotkey(hotkey.VK_HOME)
def reset_time():
    global ZERO_TIME
    ZERO_TIME = time.time()
    print('Reseting timer:', timediff2str(0))

with hotkey.EventLoop():
    handle = ctypes.windll.kernel32.FindFirstChangeNotificationW(os.path.dirname(PATH), 0, 0x11)

    try:
        while True:
            ret = ctypes.windll.kernel32.WaitForSingleObject(handle, 1000)
            ctypes.windll.kernel32.FindNextChangeNotification(handle)
            try:
                mtime = os.stat(PATH).st_mtime
                if mtime > last_modified:
                    last_modified = mtime
                    name = timediff2str(last_modified-ZERO_TIME)
                    print('Storing backup save:', name)
                    target_path = os.path.join(BACKUP_DIRECTORY, name+'.sav')
                    target_path = target_path.replace(':', '..')
                    shutil.copy(PATH, target_path)

            except FileNotFoundError:
                pass
    except KeyboardInterrupt:
        pass
    finally:
        ctypes.windll.kernel32.FindCloseChangeNotification(handle)