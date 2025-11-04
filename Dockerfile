# Use a small official Python image
FROM python:3.11-slim

# Environment settings
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

# Set working directory inside the container
WORKDIR /app

# Copy dependency list first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your source code
COPY . .

# Expose port for documentation (host maps it)
EXPOSE 8000

# Run FastAPI using uvicorn
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]
