from backend.app.main import create_app
import os

if __name__ == "__main__":
    app, socketio = create_app()
    # Disable reloader to avoid double-running expensive startup initialization.
    socketio.run(app, debug=True, port=5000, use_reloader=False, allow_unsafe_werkzeug=True)

