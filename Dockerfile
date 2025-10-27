# Use a base image that has Python and includes apt-get capabilities
FROM python:3.11-slim

# Install Tesseract OCR
RUN apt-get update \
    && apt-get install -y tesseract-ocr \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory to the project root inside the image
WORKDIR /usr/src/app

# Copy only the requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code including the backend and frontend
COPY . /usr/src/app/

# Set the final working directory to the backend where app.py lives
WORKDIR /usr/src/app/backend

# Define the start command
CMD ["gunicorn", "backend.app:app", "-b", "0.0.0.0:$PORT"]
