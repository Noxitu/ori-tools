import os


class FileWatch:
    def __init__(self, path, callback):
        self._path = path
        self._callback = callback
        self._known_stat = self.stat()

    def stat(self):
        stat = os.stat(self._path)
        return stat.st_mtime, stat.st_size

    def on_directory_update(self):
        try:
            stat = self.stat()

            if stat == self._known_stat:
                return
            
            self._callback()
        except FileNotFoundError:
            pass
