# Use a base image that has Python and includes apt-get capabilities
FROM python:3.11-slim

# Install Tesseract OCR (System Dependencies)
RUN apt-get update \
    && apt-get install -y tesseract-ocr \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory to the project root inside the image
# (Keep this here so subsequent COPY/RUN commands are relative)
WORKDIR /usr/src/app

# Python Dependencies (Cached unless requirements.txt changes) ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Layer 2: Application Code (Only changes if code changes) ---
# Copy the rest of the application code including the backend and frontend
COPY . . 

# --- Layer 3: Define the start command (using the fully qualified path) ---
# Ensure your gunicorn is installed via requirements.txt
CMD ["gunicorn", "backend.app:app", "-b", "0.0.0.0:$PORT"]
