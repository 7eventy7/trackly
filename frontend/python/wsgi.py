from flask import Flask, send_from_directory
import os
from python.main import main as tracker_main, CONFIG_DIR
import threading
import multiprocessing

# Use a shared value to track if the tracker has been started
tracker_started = multiprocessing.Value('i', 0)

def create_app():
    app = Flask(__name__, static_folder="/app/static")

    @app.route("/")
    def serve_index():
        return send_from_directory(app.static_folder, "index.html")

    @app.route("/config/<path:filename>")
    def serve_config(filename):
        return send_from_directory(CONFIG_DIR, filename)

    @app.route("/music/<path:path>")
    def serve_music(path):
        return send_from_directory("/music", path)

    @app.route("/<path:path>")
    def serve_static(path):
        return send_from_directory(app.static_folder, path)

    # Start the tracker only if it hasn't been started yet
    with tracker_started.get_lock():
        if tracker_started.value == 0:
            tracker_started.value = 1
            tracker_thread = threading.Thread(target=tracker_main, daemon=True)
            tracker_thread.start()

    return app

app = create_app()

if __name__ == "__main__":
    app.run()