FROM python:3.11-slim

# Install Tesseract OCR
RUN apt-get update \
    && apt-get install -y tesseract-ocr \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run gunicorn
CMD gunicorn backend.app:app --bind 0.0.0.0:$PORT
