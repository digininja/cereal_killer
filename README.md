# Insecure Deserialization Vulnerability Labs

A standalone, multi-container security laboratory designed to demonstrate insecure object deserialization and remote code execution (RCE) patterns across different runtime environments: **PHP 8 (Apache)** and **Node.js 18 (Express)**.

Each lab runs in an isolated container configured with proper service boundaries, non-root execution contexts where applicable, and distribution-ready packaging.

---

## Architecture Overview

| Lab Service | Environment | Host Port | Target Vulnerability Pattern |
|---|---|---|---|
| `node-lab` | Node.js 18 (Alpine), Express | `8000` | Untrusted object deserialization (`node-serialize`) |
| `php-lab` | PHP 8.2 (Debian), Apache | `8080` | Native PHP object injection (`unserialize()`) |

```text
.
├── docker-compose.yml
├── .gitignore
├── README.md
├── node-lab/
│   ├── Dockerfile
│   ├── package.json
│   ├── server.js
│   └── logs/
└── php-lab/
    ├── Dockerfile
    ├── classes.php
    ├── index.php
    └── logs/
```

---

## Prerequisites

- [Docker Engine](https://docs.docker.com/engine/install/) (v20.10+ recommended)
- [Docker Compose](https://docs.docker.com/compose/) (v2.0+)

---

## Quickstart

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/deserialization-labs.git
cd deserialization-labs
```

### 2. Build and Start the Containers

Run the compose stack in detached mode:

```bash
docker compose up -d --build
```

### 3. Access the Labs

- **Node.js Lab:** [http://localhost:8000](http://localhost:8000)
- **PHP Lab:** [http://localhost:8080](http://localhost:8080)

---

## Lab Scenarios

### 1. Node.js Lab (`:8000`)

* **Mechanism:** Express application taking serialized user preferences via URL query parameters or cookies.
* **Vulnerability:** Unsafe deserialization using vulnerable versions of `node-serialize` or custom serialization engines allowing Immediate Invocation Function Expressions (IIFE).
* **Objective:** Identify the input point, craft a serialized JavaScript payload with an invoked function object, and trigger server-side code execution.

### 2. PHP Lab (`:8080`)

* **Mechanism:** PHP application passing base64-encoded or raw serialized strings into `unserialize()`.
* **Vulnerability:** POP (Property Oriented Programming) gadget chaining through magic methods (such as `__wakeup()`, `__destruct()`, or `__toString()`) defined in `classes.php`.
* **Objective:** Review the class definitions, construct a chained gadget payload, and write arbitrary output or obtain code execution through the `logs/` directory.

---

## Managing and Resetting the Environment

Because labs modify container filesystem state (e.g., dropping proof files in `logs/`), reset the containers between runs to maintain a clean slate:

```bash
# View live application logs
docker compose logs -f

# View logs for a specific service
docker compose logs -f node-lab
docker compose logs -f php-lab

# Soft restart (flushes in-memory backdoors/routes)
docker compose restart

# Full lab reset (destroys containers, wiping dropped artifacts and in-memory states)
docker compose down && docker compose up -d

# Stop and shut down the environment
docker compose down
```

---

## Security Notice & Disclaimer

> **Warning:** This repository contains intentionally vulnerable code designed solely for educational, research, and authorized security training purposes. Do not deploy these containers to untrusted networks, production environments, or public cloud instances without network isolation.