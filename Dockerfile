# Use a base image that has Python and includes apt-get capabilities
FROM python:3.11-slim

# Install Tesseract OCR and its language packs (English/Standard)
RUN apt-get update \
    && apt-get install -y tesseract-ocr \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory to the backend folder
WORKDIR /usr/src/app/backend

# Copy requirements and install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /usr/src/app

# Define the start command
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:$PORT"]
