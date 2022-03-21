import time
import shutil
import os
import pathlib
import sys
import threading

from ori.file_watch import FileWatch
from ori.directory_watch import DirectoryWatch
from ori.delayed_trigger import DelayedTrigger


SAVE_PATH_TEMPLATE = R'C:\Users\grzeg\AppData\Local\Ori and the Blind Forest DE\saveFile{slot}.sav'
INPUT_PATH_ROOT = pathlib.Path(__file__).parent.parent.parent / 'saves'


def create_logger():
    zero = time.monotonic()

    def log(*args, **kwargs):
        print(f'[{time.monotonic() - zero:.2f}]', *args, **kwargs)
    
    return log


def create_thread(target, *, args=[], kwargs={}, daemon=False):
    th = threading.Thread(target=target, args=args, kwargs=kwargs)
    th.daemon = daemon
    th.start()
    return th


log = create_logger()


def get_args():
    name, slot = sys.argv[1:]
    slot = int(slot)

    input_path = INPUT_PATH_ROOT / name

    save_path = SAVE_PATH_TEMPLATE.format(slot=slot)

    return input_path, save_path


def main():
    source_path, target_path = get_args()

    shutil.copy2(source_path, target_path)
    source_stat = os.stat(source_path)
    source_stat = source_stat.st_mtime, source_stat.st_size

    def log_update():
        stat = fw.stat()

        if stat == source_stat:
            return

        log('Restoring file.')
        shutil.copy2(source_path, target_path)

    fw = FileWatch(target_path, DelayedTrigger(log_update, delay=10))
    dw = DirectoryWatch(os.path.dirname(target_path), fw.on_directory_update)
    
    th = create_thread(dw.start)

    log('Started...')

    try:
        while True:
            time.sleep(15)
    except KeyboardInterrupt:
        log('KeyboardInterrupt')

    dw.stop()

    th.join()
    log('Done.')



if __name__ == '__main__':
    main()
