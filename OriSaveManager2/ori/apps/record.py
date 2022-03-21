import time
import os
import pathlib
import shutil
import sys
import threading

from ori.file_watch import FileWatch
from ori.directory_watch import DirectoryWatch
from ori.delayed_trigger import DelayedTrigger
from ori.save.ori_save import OriSave


SAVE_PATH_TEMPLATE = R'C:\Users\grzeg\AppData\Local\Ori and the Blind Forest DE\saveFile{slot}.sav'
OUTPUT_PATH_ROOT = pathlib.Path(__file__).parent.parent.parent / 'saves'


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

    output_path = OUTPUT_PATH_ROOT / name

    # if output_path.exists() and len(output_path.iterdir()) > 0:
    #     raise Exception('Save path already exists')

    save_path = SAVE_PATH_TEMPLATE.format(slot=slot)

    return output_path, save_path


def main():
    output_path, save_path = get_args()
    output_path.mkdir(parents=True, exist_ok=True)
    tmp_path = output_path / 'tmp.sav'

    def log_update():
        shutil.copy2(save_path, tmp_path)

        save = OriSave(path=tmp_path)
        save_time = '{0:d}-{1:02d}-{2:02d}'
        save_time = save_time.format(*save.time)
        
        save_name = f'{save_time} {save.area_name.decode()}'
        shutil.move(tmp_path, output_path / f'{save_name}.sav')
        log('New save:', save_name)

    fw = FileWatch(save_path, DelayedTrigger(log_update, delay=0.1))
    dw = DirectoryWatch(os.path.dirname(save_path), fw.on_directory_update)
    
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
