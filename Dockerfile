# Dockerfile

# Use a lean Python base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy dependencies and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code and ABI
COPY . /app

# Expose the port Uvicorn will listen on
EXPOSE 8000

# Command to run the application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]