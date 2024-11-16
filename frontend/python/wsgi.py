import sys
import os
from flask import Flask, send_from_directory
from python.main import main as tracker_main, DATA_DIR, MUSIC_DIR
import threading
import multiprocessing

if not sys.warnoptions:
    devnull = open(os.devnull, 'w')
    sys.stdout = devnull
    sys.stderr = devnull

tracker_started = multiprocessing.Value('i', 0)

def create_app():
    static_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dist")
    app = Flask(__name__, static_folder=static_folder)

    @app.route("/data/<path:filename>")
    def serve_data(filename):
        return send_from_directory(DATA_DIR, filename)

    @app.route("/music/<path:path>")
    def serve_music(path):
        return send_from_directory(MUSIC_DIR, path)

    @app.route("/assets/<path:path>")
    def serve_assets(path):
        return send_from_directory(os.path.join(app.static_folder, "assets"), path)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_spa(path):
        if os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, "index.html")

    with tracker_started.get_lock():
        if tracker_started.value == 0:
            tracker_started.value = 1
            tracker_thread = threading.Thread(target=tracker_main, daemon=True)
            tracker_thread.start()

    return app

app = create_app()

if __name__ == "__main__":
    app.run()