import os
import sys
import base64
import pickle
import urllib.parse
from datetime import datetime
from flask import Flask, request, render_template_string, send_from_directory, abort

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'visitor-analytics.log')

# Ensure logs directory exists
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


# Model classes mimicking the PHP classes
class ThemeConfig:
    def __init__(self, color="lightblue", font="Arial"):
        self.color = color
        self.font = font


class DebugLog:
    def __init__(self, log_file=LOG_FILE):
        self.log_file = log_file
        self.log_message = f"Page accessed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    def write(self):
        try:
            with open(self.log_file, "a") as f:
                f.write(self.log_message + "\n")
        except Exception:
            pass


HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>Theme Manager Lab</title>
    <style>
        body { background-color: {{ bg_color }}; font-family: {{ font }}; padding: 20px; margin: 0; padding-bottom: 60px; }
        .container { background: rgba(255,255,255,0.9); padding: 30px; border-radius: 8px; border: 1px solid #ccc; max-width: 600px; margin: 20px auto;}
        
        .dev-toolbar { position: fixed; bottom: 0; left: 0; width: 100%; background: #222; border-top: 2px solid #444; padding: 10px 0; text-align: center; z-index: 1000; box-shadow: 0 -2px 10px rgba(0,0,0,0.5); }
        .dev-btn { background: #444; color: #0f0; border: 1px solid #555; padding: 8px 16px; margin: 0 5px; font-family: monospace; cursor: pointer; border-radius: 4px; transition: background 0.2s; }
        .dev-btn:hover { background: #555; color: #fff; }
        
        .popup-panel { display: none; position: fixed; bottom: 60px; left: 50%; transform: translateX(-50%); background: #1a1a1a; color: #0f0; padding: 20px; font-family: monospace; font-size: 13px; border-radius: 8px 8px 0 0; width: 90%; max-width: 800px; max-height: 60vh; overflow-y: auto; border: 1px solid #444; border-bottom: none; z-index: 999; box-shadow: 0 -5px 15px rgba(0,0,0,0.5); }
        .close-btn { float: right; cursor: pointer; color: #ff5555; font-weight: bold; border: 1px solid #ff5555; padding: 2px 8px; border-radius: 3px; }
        .close-btn:hover { background: #ff5555; color: #000; }
        
        .dump-box { background: #000; color: #0ff; padding: 12px; border: 1px solid #333; overflow-x: auto; margin-top: 10px; }
        .log-box { background: #000; color: #ccc; padding: 12px; border: 1px solid #333; overflow-x: auto; margin-top: 10px; white-space: pre-wrap; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Dashboard</h1>
        <p>Your current theme color is: <strong>{{ bg_color }}</strong></p>
        
        <hr>
        <h3>Lab Controls:</h3>
        <ul>
            <li><a href="?prefs={{ default_payload }}">Load Default Theme</a></li>
            <li><a href="?prefs={{ red_payload }}">Load Red Theme</a></li>
        </ul>
    </div>

    <div class="dev-toolbar">
        <button class="dev-btn" onclick="togglePanel('debug-panel')">🔧 Toggle Unserialize Engine Debugger</button>
        <button class="dev-btn" onclick="togglePanel('log-panel')">📄 Toggle System Logs</button>
    </div>

    <div id="debug-panel" class="popup-panel">
        <span class="close-btn" onclick="togglePanel('')">X</span>
        <strong>System Debug Info (Dev Mode: ON)</strong><br><br>
        Current Path: <code>{{ base_dir }}</code><br>
        Log Directory: <code>./logs/</code> 
        
        {% if is_writable %}
            <span style='color: yellow;'>[Status: WRITABLE]</span>
        {% else %}
            <span style='color: red;'>[Status: READ-ONLY]</span>
        {% endif %}
        
        <div style="margin-top: 15px;">
            <strong>Unserialize() Engine Output:</strong>
            <pre class="dump-box">{{ deserialization_debug }}</pre>
        </div>
    </div>

    <div id="log-panel" class="popup-panel">
        <span class="close-btn" onclick="togglePanel('')">X</span>
        <strong>Current visitor-analytics.log:</strong>
        <div class="log-box">{{ log_contents }}</div>
    </div>

    <script>
        function togglePanel(panelId) {
            var debugPanel = document.getElementById('debug-panel');
            var logPanel = document.getElementById('log-panel');

            if (panelId === '') {
                debugPanel.style.display = 'none';
                logPanel.style.display = 'none';
                localStorage.removeItem('activeDevPanel');
                return;
            }

            var targetPanel = document.getElementById(panelId);

            if (targetPanel.style.display === 'block') {
                targetPanel.style.display = 'none';
                localStorage.removeItem('activeDevPanel');
            } else {
                debugPanel.style.display = 'none';
                logPanel.style.display = 'none';
                targetPanel.style.display = 'block';
                localStorage.setItem('activeDevPanel', panelId);
            }
        }

        window.addEventListener('DOMContentLoaded', (event) => {
            var autoOpen = {{ 'true' if auto_open_debug else 'false' }};
            if (autoOpen) {
                togglePanel('debug-panel');
                return;
            }

            var savedPanel = localStorage.getItem('activeDevPanel');
            if (savedPanel && document.getElementById(savedPanel)) {
                document.getElementById(savedPanel).style.display = 'block';
            }
        });
    </script>
</body>
</html>"""


def serialize_payload(obj):
    raw = pickle.dumps(obj)
    return urllib.parse.quote(base64.b64encode(raw).decode('utf-8'))


@app.route("/")
def index():
    tracker = DebugLog()
    settings = ThemeConfig()
    deserialization_debug = "No input provided."
    auto_open_debug = False

    prefs = request.args.get('prefs')
    if prefs:
        try:
            decoded_data = base64.b64decode(prefs)
        except Exception:
            decoded_data = b""

        debug_lines = [
            "--- DECODED STRING ---",
            f"string({len(decoded_data)}) {repr(decoded_data)}\n",
            "--- RESULTING OBJECT ---"
        ]

        unserialized = None
        try:
            unserialized = pickle.loads(decoded_data)
            debug_lines.append(f"object({type(unserialized).__name__}) {repr(unserialized)}")
        except Exception as e:
            debug_lines.append(f"bool(false)\n\n[!] Deserialization failed. Check string syntax and URL encoding.\nException: {str(e)}")
            auto_open_debug = True

        deserialization_debug = "\n".join(debug_lines)

        if unserialized is not None:
            settings = unserialized

            if not isinstance(settings, ThemeConfig):
                auto_open_debug = True
            else:
                color_val = getattr(settings, 'color', 'unknown')
                tracker.log_message += f" | Theme loaded: {color_val}"

    tracker.write()

    log_contents = "No logs yet."
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                log_contents = f.read() or "No logs yet."
        except Exception as e:
            log_contents = f"Error reading log: {str(e)}"

    bg_color = getattr(settings, 'color', 'lightblue')
    font = getattr(settings, 'font', 'Arial')
    is_writable = os.access(LOG_DIR, os.W_OK)

    default_payload = serialize_payload(ThemeConfig())
    red_config = ThemeConfig(color="lightcoral")
    red_payload = serialize_payload(red_config)

    return render_template_string(
        HTML_TEMPLATE,
        bg_color=bg_color,
        font=font,
        base_dir=BASE_DIR,
        is_writable=is_writable,
        deserialization_debug=deserialization_debug,
        log_contents=log_contents,
        auto_open_debug=auto_open_debug,
        default_payload=default_payload,
        red_payload=red_payload
    )


@app.route("/status")
def status():
    """Simple service health check endpoint."""
    return "OK", 200


@app.route("/logs/<path:filename>")
def fetch_log(filename):
    safe_path = os.path.abspath(os.path.join(LOG_DIR, filename))
    if not safe_path.startswith(os.path.abspath(LOG_DIR)):
        abort(403)
    if not os.path.exists(safe_path) or not os.path.isfile(safe_path):
        abort(404)
    return send_from_directory(LOG_DIR, filename, mimetype='text/plain')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
