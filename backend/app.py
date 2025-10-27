"""
Flask application handles TTB label verification requests
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import logging
from .utils.ocr_processor import extract_text_from_image, test_tesseract_installation
from .utils.verification import verify_label_data
from dotenv import load_dotenv
from os import environ

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load variables from the .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')

# Enable CORS for development
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = environ.get('SECRET_KEY', 'default-fallback-key')

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    # Assuming index.html is in ../frontend/templates
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    return jsonify({"status": "ok", "message": "API is running."})

@app.route('/api/verify', methods=['POST'])
def verify():
    # 1. Input Validation (File and Form Data)
    if 'image' not in request.files:
        return jsonify({"success": False, "message": "No image file provided."}), 400
    
    file = request.files['image']
    form_data = request.form.to_dict()

    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({"success": False, "message": "Invalid or missing file."}), 400

    # 2. Save Image (Required for disk-based OCR access)
    filename = secure_filename(file.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(image_path)
    logger.info(f"Image saved to: {image_path}")

    try:
        # 3. OCR Extraction (Now uses Cloud API via ocr_processor.py)
        # Note: ocr_processor.py should be updated to use requests and a cloud API
        extracted_text = extract_text_from_image(image_path)
        
        # Handle OCR errors passed back as strings
        if extracted_text.startswith("ERROR:") or extracted_text.startswith("No readable text"):
            return jsonify({
                "success": False,
                "message": "OCR Failed or no text found.",
                "details": [
                    {
                        "field": "OCR Status",
                        "form_value": "N/A",
                        "label_value": extracted_text,
                        "status": "ERROR",
                        "message": extracted_text
                    }
                ]
            }), 200 # Return 200 but indicate failure internally

        # 4. Verification
        results = verify_label_data(form_data, extracted_text)
        
        # 5. Determine Overall Status
        overall_status = all(r['status'] == 'MATCH' for r in results)
        overall_message = "SUCCESS: All required label information matches the application form." if overall_status else "FAILURE: Discrepancies found between the label and the application form."
        
        return jsonify({
            "success": overall_status,
            "message": overall_message,
            "details": results
        }), 200

    except Exception as e:
        logger.error(f"Verification processing failed: {e}")
        return jsonify({"success": False, "message": f"Server processing error: {e}"}), 500
    
    finally:
        # 6. Clean up the uploaded image file
        if os.path.exists(image_path):
            os.remove(image_path)
            logger.info(f"Cleaned up image file: {image_path}")


def startup_checks():
    logger.info("=" * 60)
    logger.info("Starting server startup checks...")
    
    # Check upload directory
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        logger.info(f"✓ Upload directory exists: {app.config['UPLOAD_FOLDER']}")
    else:
        logger.info(f"Creating upload directory: {app.config['UPLOAD_FOLDER']}")
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    logger.info("=" * 60)
    logger.info("Server is ready!")
    logger.info("Access the application at: http://localhost:5000")
    logger.info("Health check available at: http://localhost:5000/api/health")
    logger.info("=" * 60)


if __name__ == '__main__':
    # Perform startup checks
    startup_checks()
    
    # Get port from environment variable (Render provides PORT)
    port = int(os.environ.get('PORT', 5000))
    
    # Determine if running in production
    is_production = os.environ.get('FLASK_ENV') == 'production'
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=not is_production)
