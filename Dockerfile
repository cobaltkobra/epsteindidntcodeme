# Use official Python image
FROM python:3.11

# Set working directory
WORKDIR /app

# Copy local code to the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the bot
CMD ["python", "bot.py"]
