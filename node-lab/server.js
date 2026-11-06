// server.js
const express = require('express');
const serialize = require('node-serialize');
const fs = require('fs');
const path = require('path');
const util = require('util');

const app = express();

// 1. Setup the logs directory (The Information Disclosure target)
const logDir = path.join(__dirname, 'logs');
if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
}
const logFile = path.join(logDir, 'visitor-analytics.log');

app.get('/', (req, res) => {
    // Legitimate use of the file system: logging visitors
    fs.appendFileSync(logFile, `Page accessed at ${new Date().toISOString()}\n`);

    let settings = { color: 'lightblue', font: 'Arial' };
    let deserializationDebug = "No input provided.";
    let debugLogArray = [];

    // 2. Load user preferences
    if (req.query.prefs) {
        try {
            // Decode the Base64 string
            let decodedData = Buffer.from(req.query.prefs, 'base64').toString('utf8');
            
            debugLogArray.push("--- DECODED STRING ---");
            debugLogArray.push(decodedData);
            
            // THE VULNERABILITY: Blindly unserializing untrusted data
            let unserialized = serialize.unserialize(decodedData);
            
            debugLogArray.push("\n--- RESULTING OBJECT ---");
            // util.inspect acts like PHP's var_dump() for Node objects
            debugLogArray.push(util.inspect(unserialized, { depth: null })); 
            
            if (unserialized) {
                settings = unserialized;
                fs.appendFileSync(logFile, ` | Theme loaded: ${settings.color || 'unknown'}\n`);
            }
            deserializationDebug = debugLogArray.join('\n');
            
        } catch (err) {
            debugLogArray.push("\n--- RESULTING OBJECT ---");
            debugLogArray.push("undefined");
            debugLogArray.push("\n[!] Deserialization failed. Check string syntax and encoding.");
            debugLogArray.push(`Error details: ${err.message}`);
            deserializationDebug = debugLogArray.join('\n');
        }
    }

    // 3. Prepare data for the UI
    let logContents = fs.existsSync(logFile) ? fs.readFileSync(logFile, 'utf8') : "No logs yet.";
    
    // Check if logs directory is writable to leak to the attacker
    let isWritable = false;
    try {
        fs.accessSync(logDir, fs.constants.W_OK);
        isWritable = true;
    } catch (e) {}

    // Generate the safe Base64 payloads for the normal UI buttons
    let defaultThemeStr = serialize.serialize({ color: 'lightblue', font: 'Arial' });
    let redThemeStr = serialize.serialize({ color: 'lightcoral', font: 'Arial' });
    
    let defaultTheme64 = encodeURIComponent(Buffer.from(defaultThemeStr).toString('base64'));
    let redTheme64 = encodeURIComponent(Buffer.from(redThemeStr).toString('base64'));

    // 4. Render the HTML
    res.send(`
    <!DOCTYPE html>
    <html>
    <head>
        <title>Theme Manager Lab (Node.js)</title>
        <style>
            body { background-color: ${settings.color || 'lightblue'}; font-family: ${settings.font || 'Arial'}; padding: 20px; margin: 0; padding-bottom: 60px; }
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
            <h1>Dashboard (Node.js)</h1>
            <p>Your current theme colour is: <strong>${settings.color || 'lightblue'}</strong></p>
            
            <hr>
            <h3>Lab Controls:</h3>
            <ul>
                <li><a href="?prefs=${defaultTheme64}">Load Blue Theme</a></li>
                <li><a href="?prefs=${redTheme64}">Load Red Theme</a></li>
            </ul>
        </div>

        <div class="dev-toolbar">
            <button class="dev-btn" onclick="togglePanel('debug-panel')">🔧 Toggle Unserialize Engine Debugger</button>
            <button class="dev-btn" onclick="togglePanel('log-panel')">📄 Toggle System Logs</button>
        </div>

        <div id="debug-panel" class="popup-panel">
            <span class="close-btn" onclick="togglePanel('')">X</span>
            <strong>System Debug Info (Dev Mode: ON)</strong><br><br>
            Current Path: <code>${__dirname}</code><br>
            Log Directory: <code>./logs/</code> 
            
            ${isWritable ? "<span style='color: yellow;'>[Status: WRITABLE]</span>" : "<span style='color: red;'>[Status: READ-ONLY]</span>"}
            
            <div style="margin-top: 15px;">
                <strong>Unserialize() Engine Output:</strong>
                <pre class="dump-box">${deserializationDebug.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</pre>
            </div>
        </div>

        <div id="log-panel" class="popup-panel">
            <span class="close-btn" onclick="togglePanel('')">X</span>
            <strong>Current visitor-analytics.log:</strong>
            <div class="log-box">${logContents.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</div>
        </div>

        <script>
            function togglePanel(panelId) {
                var debugPanel = document.getElementById('debug-panel');
                var logPanel = document.getElementById('log-panel');

                // If closing all panels
                if (panelId === '') {
                    debugPanel.style.display = 'none';
                    logPanel.style.display = 'none';
                    localStorage.removeItem('activeDevPanel');
                    return;
                }

                var targetPanel = document.getElementById(panelId);

                // If clicking a panel that is already open, close it
                if (targetPanel.style.display === 'block') {
                    targetPanel.style.display = 'none';
                    localStorage.removeItem('activeDevPanel');
                }
                // Otherwise, close others and open the target
                else {
                    debugPanel.style.display = 'none';
                    logPanel.style.display = 'none';
                    targetPanel.style.display = 'block';
                    localStorage.setItem('activeDevPanel', panelId);
                }
            }

            // Automatically restore the panel state when the page reloads
            window.addEventListener('DOMContentLoaded', (event) => {
                var savedPanel = localStorage.getItem('activeDevPanel');
                if (savedPanel && document.getElementById(savedPanel)) {
                    document.getElementById(savedPanel).style.display = 'block';
                }
            });
        </script>
    </body>
    </html>
    `);
});

app.listen(8000, () => console.log('Target Node server running on http://localhost:8000'));

// Handle CTRL+C gracefully for Docker
process.on('SIGINT', () => {
    console.log('\nGracefully shutting down from SIGINT (Ctrl-C)');
    process.exit(0);
});
