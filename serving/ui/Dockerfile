# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy dependency file first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose port 5001 (the one your UI runs on)
EXPOSE 5001

# Command to start the app
CMD ["python", "penguin_app_ui.py"]
