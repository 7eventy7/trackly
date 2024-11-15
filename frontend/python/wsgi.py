from flask import Flask, send_from_directory
import os
from python.main import main as tracker_main
import threading

def create_app():
    app = Flask(__name__, static_folder="/app/static")

    @app.route("/")
    def serve_index():
        return send_from_directory(app.static_folder, "index.html")

    @app.route("/config/<path:filename>")
    def serve_config(filename):
        return send_from_directory(os.path.join(app.static_folder, "config"), filename)

    @app.route("/music/<path:path>")
    def serve_music(path):
        return send_from_directory("/music", path)

    @app.route("/<path:path>")
    def serve_static(path):
        return send_from_directory(app.static_folder, path)

    # Start the tracker in a separate thread
    tracker_thread = threading.Thread(target=tracker_main, daemon=True)
    tracker_thread.start()

    return app

app = create_app()

if __name__ == "__main__":
    app.run()