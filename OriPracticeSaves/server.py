import flask
import json
import sys
import os
from flask import request
from updatesave import ori_replace_save

SAVE_SLOT_ID = int(sys.argv[1])
SAVES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saves')

app = flask.Flask(__name__, static_url_path='')

def register_file(url, path):
    @app.route(url, endpoint=path)
    def index():
        return app.send_static_file(path)

register_file('/', 'index.html')

@app.route('/activate-save', methods = ['POST'])
def activate_save():
    data = request.data.decode('utf8')
    data = json.loads(data)

    savefile = data['savefile']

    ori_replace_save(SAVE_SLOT_ID, os.path.join(SAVES_PATH, savefile))

    return '{"ok": true}'

@app.route('/saves.json')
def list_saves():
    def generator():
        for dirpath, dirnames, filenames in os.walk(SAVES_PATH):
            if not dirpath.startswith(SAVES_PATH):
                raise Exception('dirpath not in SAVES_PATH')

            rel_dirpath = dirpath[len(SAVES_PATH):].lstrip('\\')
            icons = {}
            more_info = {}

            if 'icons.txt' in filenames:
                path = os.path.join(dirpath, 'icons.txt')
                for line in open(path):
                    line = line.strip()
                    if not line: continue
                    name, _, icon = line.rpartition(' ')
                    icons[name] = icon

            if 'info.txt' in filenames:
                path = os.path.join(dirpath, 'info.txt')
                more_info = json.load(open(path))

            for filename in filenames:
                if not filename.endswith('.sav'):
                    continue

                name = filename[:-4]

                if name.startswith('save - '):
                    name = name[7:]

                name = name.replace('..', ':')

                data = {
                    'name': name,
                    'file': os.path.join(rel_dirpath, filename),
                    'icon': icons.get(name, 'sd_storage'),
                    'group': rel_dirpath
                }

                data.update(more_info.get(name, {}))

                yield data

    return json.dumps({'save_list': list(generator())})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)