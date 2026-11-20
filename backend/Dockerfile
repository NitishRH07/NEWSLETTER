FROM mcr.microsoft.com/playwright/python:v1.47.0-noble

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure Playwright browser is installed
RUN playwright install chromium

# Copy full application code
COPY . .

# Expose container port
EXPOSE 8000

# Start FastAPI server on dynamic Render PORT
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
