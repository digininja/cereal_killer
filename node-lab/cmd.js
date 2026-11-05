const { execSync } = require('child_process');

try {
    // Run a simple command and capture the output
    const output = execSync('ls -la');
    
    // The output is a Buffer, so convert it to a string
    console.log(output.toString());
} catch (error) {
    // If the command fails (e.g., returns a non-zero exit code), it throws an error
    console.error("Command failed:", error.message);
}
