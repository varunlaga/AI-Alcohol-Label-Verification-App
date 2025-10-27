"""
Flask application handles TTB label verification requests
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import logging
from utils.ocr_processor import extract_text_from_image, test_tesseract_installation
from utils.verification import verify_label_data
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
    """
    Check if the uploaded file has an allowed extension
    
    Args:
        filename: Name of the uploaded file
        
    Returns:
        bool: True if file extension is allowed
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """
    Render the main application page
    
    Returns:
        Rendered HTML template
    """
    logger.info("Rendering index page")
    return render_template('index.html')


@app.route('/api/verify', methods=['POST'])
def verify_label():
    """
    API endpoint to verify alcohol label against form data
    
    Accepts:
        - Form data: brandName, productType, alcoholContent, netContents
        - File: labelImage
        
    Returns:
        JSON response with verification results
    """
    try:
        logger.info("=" * 60)
        logger.info("Received label verification request")
        
        # Validate image file presence
        if 'labelImage' not in request.files:
            logger.warning("No image file in request")
            return jsonify({
                'error': 'No image file uploaded. Please select a label image.'
            }), 400
        
        file = request.files['labelImage']
        
        # Validate file selection
        if file.filename == '':
            logger.warning("Empty filename")
            return jsonify({
                'error': 'No file selected. Please choose an image file.'
            }), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            logger.warning(f"Invalid file type: {file.filename}")
            return jsonify({
                'error': 'Invalid file type. Please upload a PNG or JPEG image.'
            }), 400
        
        # Extract form data
        form_data = {
            'brand_name': request.form.get('brandName', '').strip(),
            'product_type': request.form.get('productType', '').strip(),
            'alcohol_content': request.form.get('alcoholContent', '').strip(),
            'net_contents': request.form.get('netContents', '').strip()
        }
        
        logger.info(f"Form data received:")
        logger.info(f"  - Brand Name: {form_data['brand_name']}")
        logger.info(f"  - Product Type: {form_data['product_type']}")
        logger.info(f"  - Alcohol Content: {form_data['alcohol_content']}%")
        logger.info(f"  - Net Contents: {form_data['net_contents'] or 'Not provided'}")
        
        # Validate required fields
        if not form_data['brand_name']:
            return jsonify({
                'error': 'Brand name is required'
            }), 400
        
        if not form_data['product_type']:
            return jsonify({
                'error': 'Product class/type is required'
            }), 400
        
        if not form_data['alcohol_content']:
            return jsonify({
                'error': 'Alcohol content is required'
            }), 400
        
        # Validate alcohol content is a valid number
        try:
            abv = float(form_data['alcohol_content'])
            if abv < 0 or abv > 100:
                return jsonify({
                    'error': 'Alcohol content must be between 0 and 100'
                }), 400
        except ValueError:
            return jsonify({
                'error': 'Alcohol content must be a valid number'
            }), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        logger.info(f"File saved temporarily: {filepath}")
        
        try:
            # Extract text from image using OCR (Tesseract)
            logger.info("Starting OCR text extraction...")
            extracted_text = extract_text_from_image(filepath)
            
            logger.info(f"OCR extraction completed: {len(extracted_text)} characters")
            logger.debug(f"Extracted text preview:\n{extracted_text[:300]}...")
            
            # Check if sufficient text was extracted
            if not extracted_text or len(extracted_text.strip()) < 50:
                logger.warning("Insufficient text extracted from image")
                return jsonify({
                    'error': 'Could not read sufficient text from the label image. '
                            'Please ensure the image is clear, well-lit, and contains readable text. '
                            'Try taking a higher quality photo or using a clearer image.'
                }), 400
            
            # Verify label data against form inputs
            logger.info("Starting label verification...")
            verification_results = verify_label_data(form_data, extracted_text)
            
            # Log results summary
            match_count = sum(1 for v in verification_results if v['status'] == 'match')
            total_count = len(verification_results)
            logger.info(f"Verification completed: {match_count}/{total_count} checks passed")
            
            for result in verification_results:
                logger.info(f"  - {result['field']}: {result['status']}")
            
            # Return results
            response = {
                'success': True,
                'verifications': verification_results,
                'extracted_text': extracted_text[:1000]  # Limit to first 1000 chars
            }
            
            logger.info("Request processed successfully")
            logger.info("=" * 60)
            
            return jsonify(response), 200
        
        finally:
            # Clean up temporary file
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Cleaned up temporary file: {filepath}")
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({
            'error': f'An unexpected error occurred while processing your request. '
                    f'Please try again or contact support if the problem persists. '
                    f'Error details: {str(e)}'
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify server and Tesseract status
    
    Returns:
        JSON response with server status
    """
    tesseract_ok = test_tesseract_installation()
    
    return jsonify({
        'status': 'healthy' if tesseract_ok else 'degraded',
        'tesseract_installed': tesseract_ok,
        'message': 'Server is running' if tesseract_ok else 'Tesseract OCR not found'
    }), 200 if tesseract_ok else 503


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file size exceeded error"""
    logger.warning("File size exceeded 16MB limit")
    return jsonify({
        'error': 'File is too large. Maximum size is 16MB. '
                'Please compress your image or use a smaller file.'
    }), 413


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'error': 'Internal server error. Please try again later.'
    }), 500


def startup_checks():
    """
    Perform startup checks to ensure system is ready
    """
    logger.info("=" * 60)
    logger.info("TTB Label Verification App - Startup")
    logger.info("=" * 60)
    
    # Check Tesseract installation
    logger.info("Checking Tesseract OCR installation...")
    if test_tesseract_installation():
        logger.info("✓ Tesseract OCR is properly installed and working")
    else:
        logger.error("✗ Tesseract OCR is not installed or not accessible")
        logger.error("Please install Tesseract from:")
        logger.error("  Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        logger.error("  macOS: brew install tesseract")
        logger.error("  Linux: sudo apt-get install tesseract-ocr")
        logger.error("")
        logger.error("After installation, if Tesseract is not in PATH:")
        logger.error("  Edit backend/utils/ocr_processor.py and uncomment:")
        logger.error("  pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'")
    
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
    
    logger.info(f"Starting Flask server on port {port}...")
    logger.info(f"Environment: {'Production' if is_production else 'Development'}")
    
    app.run(
        debug=not is_production,  # Debug off in production
        host='0.0.0.0',
        port=port
    )
