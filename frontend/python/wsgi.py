from flask import Flask, send_from_directory
import os
from python.main import main as tracker_main, CONFIG_DIR
import threading
import multiprocessing

# Use a shared value to track if the tracker has been started
tracker_started = multiprocessing.Value('i', 0)

def create_app():
    # Update static folder to point to the React build directory
    static_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dist")
    app = Flask(__name__, static_folder=static_folder)

    @app.route("/config/<path:filename>")
    def serve_config(filename):
        return send_from_directory(CONFIG_DIR, filename)

    @app.route("/music/<path:path>")
    def serve_music(path):
        return send_from_directory("/music", path)

    # Serve static files from the React build
    @app.route("/assets/<path:path>")
    def serve_assets(path):
        return send_from_directory(os.path.join(app.static_folder, "assets"), path)

    # Catch-all route to serve index.html for client-side routing
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_spa(path):
        # If the path exists as a file, serve it directly
        if os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        # Otherwise, serve index.html for client-side routing
        return send_from_directory(app.static_folder, "index.html")

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