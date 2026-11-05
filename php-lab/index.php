<?php
// index.php
require_once 'classes.php';

$tracker = new DebugLog();
$tracker->logFile = "logs/visitor-analytics.log";
$tracker->logMessage = "Page accessed at " . date('Y-m-d H:i:s');

$settings = new ThemeConfig();
$deserializationDebug = "No input provided.";
$autoOpenDebug = false; // NEW: Flag to control the popup

if (isset($_GET['prefs'])) {
    $decodedData = base64_decode($_GET['prefs']);
    
    ob_start();
    echo "--- DECODED STRING ---\n";
    var_dump($decodedData);
    
    $unserialized = @unserialize($decodedData); // VULNERABILITY
    
    echo "\n--- RESULTING OBJECT ---\n";
    var_dump($unserialized);
    
    // ANOMALY 1: The string was corrupted (bad encoding/syntax)
    if ($unserialized === false && $decodedData !== serialize(false)) {
        echo "\n[!] Deserialization failed. Check string syntax and URL encoding.";
        $autoOpenDebug = true; 
    }
    
    $deserializationDebug = ob_get_clean();
    
    if ($unserialized) {
        $settings = $unserialized;
        
        // ANOMALY 2: The object instantiated isn't a ThemeConfig! (Exploit Success)
        if (!($settings instanceof ThemeConfig)) {
            $autoOpenDebug = true;
        } else {
            // Normal behavior
            $tracker->logMessage .= " | Theme loaded: " . htmlspecialchars($settings->color ?? 'unknown');
        }
    }
}

$bgColor = htmlspecialchars($settings->color ?? 'lightblue');
$font = htmlspecialchars($settings->font ?? 'Arial');

$logPath = __DIR__ . '/logs/visitor-analytics.log';
$logContents = file_exists($logPath) ? file_get_contents($logPath) : "No logs yet.";
?>

<!DOCTYPE html>
<html>
<head>
    <title>Theme Manager Lab</title>
    <style>
        body { background-color: <?php echo $bgColor; ?>; font-family: <?php echo $font; ?>; padding: 20px; margin: 0; padding-bottom: 60px; }
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
        <p>Your current theme color is: <strong><?php echo $bgColor; ?></strong></p>
        
        <hr>
        <h3>Lab Controls:</h3>
        <ul>
            <li><a href="?prefs=<?php echo urlencode(base64_encode(serialize(new ThemeConfig()))); ?>">Load Default Theme</a></li>
            <?php 
                $redTheme = new ThemeConfig();
                $redTheme->color = "lightcoral";
            ?>
            <li><a href="?prefs=<?php echo urlencode(base64_encode(serialize($redTheme))); ?>">Load Red Theme</a></li>
        </ul>
    </div>

    <div class="dev-toolbar">
        <button class="dev-btn" onclick="togglePanel('debug-panel')">🔧 Toggle Unserialize Engine Debugger</button>
        <button class="dev-btn" onclick="togglePanel('log-panel')">📄 Toggle System Logs</button>
    </div>

    <div id="debug-panel" class="popup-panel">
        <span class="close-btn" onclick="togglePanel('')">X</span>
        <strong>System Debug Info (Dev Mode: ON)</strong><br><br>
        Current Path: <code><?php echo __DIR__; ?></code><br>
        Log Directory: <code>./logs/</code> 
        
        <?php 
        if (is_writable(__DIR__ . '/logs')) {
            echo "<span style='color: yellow;'>[Status: WRITABLE]</span>";
        } else {
            echo "<span style='color: red;'>[Status: READ-ONLY]</span>";
        }
        ?>
        
        <div style="margin-top: 15px;">
            <strong>Unserialize() Engine Output:</strong>
            <pre class="dump-box"><?php echo htmlspecialchars($deserializationDebug); ?></pre>
        </div>
    </div>

    <div id="log-panel" class="popup-panel">
        <span class="close-btn" onclick="togglePanel('')">X</span>
        <strong>Current visitor-analytics.log:</strong>
        <div class="log-box"><?php echo htmlspecialchars($logContents); ?></div>
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
