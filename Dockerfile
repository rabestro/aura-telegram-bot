# Use an official lightweight Python image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the file with dependencies
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot script into the container
COPY echo_bot.py .

# Command to run the bot when the container starts
CMD ["python", "echo_bot.py"]
