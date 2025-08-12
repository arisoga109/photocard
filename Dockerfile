# Stage 1: Build Stage
# Use a larger Python image with build tools
FROM python:3.10 as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production Stage
# Use a smaller, cleaner image for the final app
FROM python:3.10-slim

# Copy only the necessary files from the builder stage
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY . .

# Expose the port Gunicorn will listen on
EXPOSE 8000

# Command to run the application with Gunicorn using a single worker to save memory
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "app:app", "--workers", "1"]
