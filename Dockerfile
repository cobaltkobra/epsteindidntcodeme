FROM python:3.11-slim

# Environment settings for faster logs + cleaner builds
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies needed for pip builds
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies first to cache layers
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy all files
COPY . .

# Default run command
CMD ["python", "bot.py"]
