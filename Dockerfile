# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY . .

# Expose port
EXPOSE 8000

# Command to run the application - sesuaikan path ke main.py di folder app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]