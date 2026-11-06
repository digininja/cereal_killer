# Use a lightweight Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy dependency file and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Ensure the logs directory exists and has the right permissions
RUN mkdir -p logs && chmod 777 logs

# Expose the port Flask runs on
EXPOSE 5000

# Run the application
CMD ["python", "server.py"]
