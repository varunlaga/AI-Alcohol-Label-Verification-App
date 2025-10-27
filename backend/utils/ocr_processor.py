"""
OCR Processor handles text extraction from label images using a Cloud OCR API.
"""

import logging
import requests
import os 
from io import BytesIO

logger = logging.getLogger(__name__)

# --- Cloud OCR Configuration ---
# NOTE: Using the public 'helloworld' key for demonstration.
OCR_API_URL = 'https://api.ocr.space/parse/image'
OCR_API_KEY = 'helloworld' 
# -------------------------------

def extract_text_from_image(image_path):
    """
    Sends the image file to the OCR.space API for text extraction.
    
    Args:
        image_path (str): Path to the image file saved in the 'uploads' folder.
        
    Returns:
        str: Extracted text from the image, or an error message.
    """
    try:
        logger.info(f"Starting Cloud OCR processing for: {image_path}")
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Open the image file to send its content in the request
        with open(image_path, 'rb') as f:
            image_bytes = f.read()

        # Filename is required for the API; we pass the bytes content
        files = {'filename': (os.path.basename(image_path), image_bytes)}
        
        payload = {
            'apikey': OCR_API_KEY,
            'language': 'eng',
            'isOverlayRequired': 'true', 
        }

        # Make the API call
        response = requests.post(OCR_API_URL, files=files, data=payload)
        response.raise_for_status()
        data = response.json()

        # Parse the response
        if data.get('ParsedResults') and data['ParsedResults'][0]['ParsedText']:
            extracted_text = data['ParsedResults'][0]['ParsedText']
            logger.info("Successfully extracted text from label.")
            return extracted_text
        elif data.get('ErrorMessage'):
             logger.error(f"OCR API Error: {data['ErrorMessage']}")
             return f"OCR Error: {data['ErrorMessage']}"
        else:
            logger.warning("OCR API returned no text and no error.")
            # If the API returns a response but no text, it usually means the text was unreadable.
            return "No readable text found on the label."

    except requests.exceptions.RequestException as e:
        logger.error(f"OCR API Request failed: {e}")
        return "ERROR: Could not connect to external OCR service."
    except Exception as e:
        logger.error(f"General error during OCR processing: {str(e)}")
        return f"ERROR: Processing failed - {str(e)}"

# This placeholder function is kept to prevent errors in app.py's startup checks
def test_tesseract_installation():
    """ Placeholder to prevent errors in app.py startup checks. """
    return True 
