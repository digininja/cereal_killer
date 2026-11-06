# Multi-Language Deserialization Lab Suite

An educational training environment designed to explore serialization mechanisms, runtime application behavior, and insecure deserialization vulnerabilities across multiple technology stacks.

This suite provides isolated, containerized applications in Python, Node.js, and PHP. Each lab demonstrates how different languages handle object state and routing, allowing researchers to practice techniques like in-memory manipulation and monkey-patching.

## 🚀 Lab Environments

The suite runs locally via Docker Compose. Each language lab is exposed on a dedicated port:

| Language / Framework | Port | Primary Vector | Description | 
| ----- | ----- | ----- | ----- | 
| **Python (Flask)** | `5000` | `pickle` | Demonstrates Python object deserialization via the `?prefs=` parameter. Features a dynamically patched `/status` endpoint and a custom developer debugging panel. | 
| **Node.js (Express)** | `8000` | Node Deserialization | Explores JavaScript object lifecycles, prototype pollution, and Express middleware manipulation. | 
| **PHP (Apache)** | `8080` | `unserialize()` | Focuses on PHP magic methods (e.g., `__wakeup`, `__destruct`) and property oriented programming (POP) chains. | 

## 🛠️ Prerequisites

* [Docker](https://docs.docker.com/get-docker/)

* [Docker Compose](https://docs.docker.com/compose/install/)

## 🚦 Getting Started

### Option 1: Using the Start Script (Recommended)

The easiest way to build the images and start the suite is using the provided bash script. This will start the containers in the background and output the access URLs.

```
chmod +x start.sh
./start.sh

```

### Option 2: Manual Docker Compose

If you prefer running it directly (or are on Windows without WSL), run:

```
docker compose up --build

```

*Note: Add `-d` to run in detached mode.*

### Option 3: Running Pre-built Images Directly

If you just want to play with the labs without downloading the source code or building the images yourself, you can pull and run the pre-built containers directly from the GitHub Container Registry (GHCR):

**Python (Flask) Lab:**

```
docker run -d -p 5000:5000 --name python-lab ghcr.io/digininja/digininja/python-lab:latest

```

*Access at: `http://localhost:5000`*

**Node.js (Express) Lab:**

```
docker run -d -p 8000:8000 --name node-lab ghcr.io/digininja/digininja/node-lab:latest

```

*Access at: `http://localhost:8000`*

**PHP (Apache) Lab:**

```
docker run -d -p 8080:80 --name php-lab ghcr.io/digininja/digininja/php-lab:latest

```

*Access at: `http://localhost:8080`*

*(Note: To stop and remove an individual lab, run `docker rm -f <container-name>`)*

## 🐍 Python Lab Focus: Flask & Pickle

The Python lab simulates a dashboard where user preferences (like UI themes) are serialized and passed via the URL.

* **Target URL**: `http://localhost:5000/`

* **Vulnerability**: The application takes base64-encoded, URL-encoded payload via the `?prefs=` query parameter and processes it using Python's native `pickle.loads()`.

* **Points of Interest**:

  * Flask explicitly locks routing (`app.add_url_rule`) after the first request.

  * The lab includes a `/status` endpoint intended for health checks, which can be used as a target for in-memory handler patching (monkey-patching the `app.view_functions` dictionary).

  * A built-in developer toolbar displays the `unserialize()` engine output to help craft and debug payloads in real-time.

## 🟢 Node.js Lab Focus: Express & Deserialization

The Node.js lab explores how JavaScript handles object serialization and runtime manipulation within the Express.js framework.

* **Target URL**: `http://localhost:8000/`

* **Vulnerability**: Demonstrates the risks of unsafe parsing libraries (such as `node-serialize`) which can evaluate serialized JavaScript functions upon deserialization.

* **Points of Interest**:

  * Explores Immediately Invoked Function Expressions (IIFEs) used to trigger execution during the deserialization phase.

  * Demonstrates the mutability of the Express routing stack (`app._router.stack`), illustrating how middleware and routes can be dynamically altered at runtime.

  * Highlights prototype pollution vectors as an alternative to direct code execution.

## 🐘 PHP Lab Focus: Magic Methods & POP Chains

The PHP lab focuses on the classic `unserialize()` vulnerability, common in legacy applications and content management systems.

* **Target URL**: `http://localhost:8080/`

* **Vulnerability**: Direct user input is passed into the native `unserialize()` function, allowing attackers to instantiate arbitrary classes already loaded in the environment.

* **Points of Interest**:

  * Heavy focus on PHP "Magic Methods" (e.g., `__construct`, `__destruct`, `__wakeup`, `__toString`).

  * Requires building a Property Oriented Programming (POP) chain by stringing together existing application classes to achieve file reads or code execution.

  * Showcases the exact string-based serialization format used by PHP (e.g., `O:4:"User":2:{...}`).

## 🛑 Stopping the Labs

To safely stop and remove the running containers, networks, and volumes if using Docker Compose:

```
docker compose down

```

## 🔓 Exploitation Guide

I've developed a set of exploits for each framework, they are stored in the directory with the server files and all start with `exploit-`. Below is a description of each.

I will be creating a set of videos to go with this lab and will add the link here once complete.

### Python

- [exploit-run_command.py](python-lab/exploit-run_command.py) - A basic script which uses the Python `os.system` function to run the `echo` command and write an entry to the log file.
- [exploit-leak_routes.py](python-lab/exploit-leak_routes.py) - A script to leak a list of endpoints available on the application. These will then be used in the monkey patch exploit.
- [exploit-monkey_patch_route.py](python-lab/exploit-monkey_patch_route.py) - This script will modify the function called by a given endpoint to point to one dynamically added to the app. The new function acts as a shim for the old one, if the query string parameter `cmd` is passed, it takes it and runs the command using the `os.system` function, otherwise it hands control back to the original function making the backdoor transparent to normal users.

### Node.js

- [exploit-run_command.js](node-lab/exploit-run_command.js) - Uses command execution to run the system `echo` command and add a line to the system log file.
- [exploit-injection.js](node-lab/exploit-injection.js) - Dynamically adds a new endpoint called `/backdoor` which runs commands passed to it in the `cmd` query string parameter.

### PHP

- [exploit-run_command.php](php-lab/exploit-run_command.php) - Drops a PHP script called `shell.php` in the writeable logs directory. This script can then be called with the `cmd` query string parameter to run arbitrary command using the PHP `system` function.

## 📝 Development Notes

* **Live Logs**: Each container mounts a fresh logging directory on startup. Local dev logs are excluded via `.dockerignore` to prevent container pollution. To view live server logs across all apps, run `docker compose logs -f`.

* **Hot Reloading**: If configured in `docker compose.yml`, local directories are volume-mounted into the containers. Saving a file locally will reflect immediately in the labs (Flask is set to `debug=True` for auto-reloading).
