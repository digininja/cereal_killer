#!/bin/bash
echo "Building and starting the multi-language lab suite..."
docker compose up --build -d

echo ""
echo "======================================================"
echo "      LAB ENVIRONMENT SUCCESSFULLY STARTED            "
echo "======================================================"
echo " Python (Flask) Lab : http://localhost:5000"
echo " Node.js Lab        : http://localhost:8000"
echo " PHP Lab            : http://localhost:8080"
echo "======================================================"
echo "To view live logs, run: docker compose logs -f"
echo "To stop the labs, run:  docker compose down"
