<?php
// classes.php

// A safe, normal class intended to be used by the application
class ThemeConfig {
    public $color = "lightblue";
    public $font = "Arial";
}

// THE GADGET: A debug class left in the codebase by mistake.
// It writes to a file when the object is destroyed by PHP's garbage collector.
class DebugLog {
    public $logFile = "logs/app-debug.txt";
    public $logMessage = "Session started.";

    public function __destruct() {
        // Appends the log message to the specified file
        file_put_contents(__DIR__ . '/' . $this->logFile, $this->logMessage . "\n", FILE_APPEND);
    }
}
?>
