# Lightweight Python base image
FROM python:3.12-slim

# Working directory inside the container
WORKDIR /app

# Copy app.py, requirements.txt and superkart_model.joblib into the image
COPY . .

# Install dependencies without caching wheels (smaller image)
RUN pip install --no-cache-dir -r requirements.txt

# Serve the Flask app with gunicorn: 4 workers, listening on port 7860 on all interfaces
EXPOSE 7860
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:superkart_api"]
