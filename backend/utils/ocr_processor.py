"""
OCR Processor handles text extraction from label images using a Cloud OCR API.
Uses requests to send the image data to OCR.space API.
"""

import logging
import requests
import os 
import time

logger = logging.getLogger(__name__)

# --- Cloud OCR Configuration ---
# NOTE: Using the public 'helloworld' key for demonstration.
OCR_API_URL = 'https://api.ocr.space/parse/image'
# IMPORTANT: If you are getting a 400 or 429 error, you may need to register 
# for your own free API key at ocr.space and replace 'helloworld'.
OCR_API_KEY = 'helloworld' 
# -------------------------------

def extract_text_from_image(image_path):
    """
    Sends the image file to the OCR.space API for text extraction.
    
    Args:
        image_path (str): Path to the image file saved in the 'uploads' folder.
        
    Returns:
        str: Extracted text from the image, or an error message prefixed with "ERROR:".
    """
    
    if not os.path.exists(image_path):
        error_msg = f"ERROR: Image file not found at path: {image_path}"
        logger.error(error_msg)
        return error_msg
    
    try:
        logger.info(f"Starting Cloud OCR processing for: {os.path.basename(image_path)}")

        # Open the image file to send its content in the request
        with open(image_path, 'rb') as f:
            image_bytes = f.read()

        # Filename is required for the API
        files = {'filename': (os.path.basename(image_path), image_bytes)}
        
        payload = {
            'apikey': OCR_API_KEY,
            'language': 'eng',
            'isOverlayRequired': 'true', 
        }

        # Make the API call
        response = requests.post(OCR_API_URL, files=files, data=payload, timeout=30)
        
        # Check for HTTP errors (4xx or 5xx)
        response.raise_for_status() 
        
        data = response.json()
        
        # Log the full API response for debugging
        logger.debug(f"OCR API Raw Response: {data}")

        # Parse the response
        if data.get('ParsedResults') and data['ParsedResults'][0]['ParsedText']:
            extracted_text = data['ParsedResults'][0]['ParsedText']
            logger.info("Successfully extracted text from label.")
            return extracted_text
            
        elif data.get('ErrorMessage'):
             # API returned a 200 but processing error occurred
             error_msg = f"OCR API Processing Error: {data['ErrorMessage']}"
             logger.error(error_msg)
             return f"ERROR: {error_msg}"
             
        elif data.get('IsErroredOnProcessing'):
             error_msg = f"OCR API General Error: {data.get('ErrorMessage', 'Unknown Processing Error')}"
             logger.error(error_msg)
             return f"ERROR: {error_msg}"
        else:
            # Catch scenario where no text is found, but no explicit error is returned
            logger.warning("OCR API returned no explicit error, but no readable text was found.")
            return "No readable text found on the label."

    except requests.exceptions.HTTPError as e:
        # Catch 4xx (Client Error) or 5xx (Server Error) responses
        error_msg = f"OCR API HTTP Error: {e.response.status_code} - {e.response.reason}. Response: {e.response.text}"
        logger.error(error_msg)
        return f"ERROR: {error_msg}"
    
    except requests.exceptions.RequestException as e:
        # Catch connection failures, timeouts, etc.
        error_msg = f"OCR API Request failed (Network/Timeout): {e}"
        logger.error(error_msg)
        return f"ERROR: Could not connect to external OCR service. {e.__class__.__name__}"
        
    except Exception as e:
        # Catch all other exceptions (JSON parsing, file read, etc.)
        error_msg = f"General error during OCR processing: {str(e)}"
        logger.error(error_msg)
        return f"ERROR: Processing failed - {str(e)}"

# Placeholder function, kept for backward compatibility in app.py's startup check
def test_tesseract_installation():
    """ Placeholder to prevent errors in app.py startup checks. """
    return True
