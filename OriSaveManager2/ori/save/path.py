import os
import pathlib


DEFAULT_GAME = 'Ori and the Blind Forest DE'


def get_default_path(game=DEFAULT_GAME):
    appdata = os.environ.get('LOCALAPPDATA')

    if appdata is None:
        return

    return pathlib.Path(appdata) / game


DEFAULT_PATH = get_default_path()
