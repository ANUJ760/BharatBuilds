FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
# Since the app is structured to run as `uvicorn backend.main:app` from the root,
# we need to preserve the `backend` directory structure.
COPY . /app/backend
ENV PYTHONPATH=/app

# Expose port 8000
EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
