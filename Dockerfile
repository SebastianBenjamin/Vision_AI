FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Set environment variables
ENV PORT=8080

# Expose the port
EXPOSE $PORT

# Command to run the API
CMD ["gunicorn", "--workers=1", "--timeout=120", "--bind=0.0.0.0:$PORT", "app:app"]
