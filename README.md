# Multi-Language Deserialization Lab Suite

An educational training environment designed to explore serialization mechanisms, runtime application behavior, and insecure deserialization vulnerabilities across multiple technology stacks. 

This suite provides isolated, containerized applications in Python, Node.js, and PHP. Each lab demonstrates how different languages handle object state and routing, allowing researchers to practice techniques like in-memory manipulation and monkey-patching.

## 🚀 Lab Environments

The suite runs locally via Docker Compose. Each language lab is exposed on a dedicated port:

| Language / Framework | Port | Primary Vector | Description |
| :--- | :--- | :--- | :--- |
| **Python (Flask)** | `5000` | `pickle` | Demonstrates Python object deserialization via the `?prefs=` parameter. Features a dynamically patched `/status` endpoint and a custom developer debugging panel. |
| **Node.js (Express)** | `8000` | Node Deserialization | Explores JavaScript object lifecycles, prototype pollution, and Express middleware manipulation. |
| **PHP (Apache)** | `8080` | `unserialize()` | Focuses on PHP magic methods (e.g., `__wakeup`, `__destruct`) and property oriented programming (POP) chains. |

---

## 🛠️ Prerequisites

* [Docker](https://docs.docker.com/get-docker/)
* [Docker Compose](https://docs.docker.com/compose/install/)

---

## 🚦 Getting Started

### Option 1: Using the Start Script (Recommended)
The easiest way to build the images and start the suite is using the provided bash script. This will start the containers in the background and output the access URLs.

```bash
chmod +x start.sh
./start.sh
```

### Option 2: Manual Docker Compose
If you prefer running it directly (or are on Windows without WSL), run:

```bash
docker-compose up --build
```
*Note: Add `-d` to run in detached mode.*

---

## 🐍 Python Lab Focus: Flask & Pickle

The Python lab simulates a dashboard where user preferences (like UI themes) are serialized and passed via the URL. 

* **Target URL**: `http://localhost:5000/`
* **Vulnerability**: The application takes base64-encoded, URL-encoded payload via the `?prefs=` query parameter and processes it using Python's native `pickle.loads()`.
* **Points of Interest**: 
  * Flask explicitly locks routing (`app.add_url_rule`) after the first request. 
  * The lab includes a `/status` endpoint intended for health checks, which can be used as a target for in-memory handler patching (monkey-patching the `app.view_functions` dictionary).
  * A built-in developer toolbar displays the `unserialize()` engine output to help craft and debug payloads in real-time.

---

## 🛑 Stopping the Labs

To safely stop and remove the running containers, networks, and volumes:

```bash
docker-compose down
```

## 📝 Development Notes

* **Live Logs**: Each container mounts a fresh logging directory on startup. Local dev logs are excluded via `.dockerignore` to prevent container pollution. To view live server logs across all apps, run `docker-compose logs -f`.
* **Hot Reloading**: If configured in `docker-compose.yml`, local directories are volume-mounted into the containers. Saving a file locally will reflect immediately in the labs (Flask is set to `debug=True` for auto-reloading).
