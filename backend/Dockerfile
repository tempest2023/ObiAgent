# IMPORTANT: Build this Docker image from the ObiAgent/backend directory.Add commentMore actions
# The requirements.txt file must be present in this directory for the build to succeed.
# Example:
#   cd ObiAgent/backend
#   docker build -t your-image-name .
 
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend code
COPY ./agent ./agent
COPY server.py .
COPY ./static ./static

# Copy requirements
COPY ./requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r ./agent/requirements.txt

# Expose port
EXPOSE 8000

# Set environment variables (override in production as needed)
ENV PYTHONUNBUFFERED=1

# Start the server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"] 