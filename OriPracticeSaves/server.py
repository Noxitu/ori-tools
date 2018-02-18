import flask
import json
import sys
import os
from flask import request
from updatesave import ori_replace_save

SAVE_SLOT_ID = int(sys.argv[1])

app = flask.Flask(__name__, static_url_path='')

def register_file(url, path):
    @app.route(url, endpoint=path)
    def index():
        return app.send_static_file(path)

register_file('/', 'index.html')
register_file('/saves.json', 'saves.json')

@app.route('/activate-save', methods = ['POST'])
def activate_save():
    data = request.data.decode('utf8')
    data = json.loads(data)

    savefile = data['savefile']

    ori_replace_save(SAVE_SLOT_ID, os.path.join('saves', savefile))

    return '{"ok": true}'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)