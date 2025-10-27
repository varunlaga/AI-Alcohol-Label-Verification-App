"""
OCR Processor handles text extraction from label images using Tesseract OCR
"""

import pytesseract
from PIL import Image
import os
import sys
import logging

logger = logging.getLogger(__name__)

# Configure Tesseract path based on OS
if sys.platform == 'win32':
    # Windows
    pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
elif sys.platform == 'darwin':
    # macOS usually in PATH after brew install
    pass
else:
    # Linux (for Render/Heroku deployment)
    # Tesseract installed via: apt-get install tesseract-ocr
    pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

def extract_text_from_image(image_path):
    """
    Extract text from an image using Tesseract OCR
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: Extracted text from the image
        
    Raises:
        Exception: If OCR processing fails
    """
    try:
        logger.info(f"Starting OCR processing for: {image_path}")
        
        # Verify file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Open image with PIL
        image = Image.open(image_path)
        logger.info(f"Image opened successfully. Size: {image.size}, Mode: {image.mode}")
        
        # Preprocess image for better OCR results
        processed_image = preprocess_image(image)
        
        # Configure OCR settings for better accuracy
        # --psm 6: Assume a single uniform block of text
        # --oem 3: Use both legacy and LSTM OCR engine modes
        custom_config = r'--oem 3 --psm 6'
        
        # Extract text using Tesseract
        extracted_text = pytesseract.image_to_string(
            processed_image,
            config=custom_config
        )
        
        logger.info(f"OCR completed. Extracted {len(extracted_text)} characters")
        logger.debug(f"Extracted text preview: {extracted_text[:200]}...")
        
        if not extracted_text or len(extracted_text.strip()) < 5:
            logger.warning("Very little text extracted from image")
            raise ValueError("Could not extract sufficient text from the image. The image may be unclear or not contain readable text.")
        
        return extracted_text
    
    except pytesseract.TesseractNotFoundError:
        logger.error("Tesseract not found on system")
        raise Exception(
            "Tesseract OCR is not installed or not found in PATH. "
            "Please install Tesseract OCR from: "
            "https://github.com/UB-Mannheim/tesseract/wiki"
        )
    
    except Exception as e:
        logger.error(f"Error during OCR processing: {str(e)}", exc_info=True)
        raise


def preprocess_image(image):
    """
    Preprocess image to improve OCR accuracy
    
    Args:
        image (PIL.Image): Input image
        
    Returns:
        PIL.Image: Preprocessed image
    """
    try:
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize image if it's too small (improves OCR accuracy)
        width, height = image.size
        min_dimension = 1000
        
        if width < min_dimension or height < min_dimension:
            scale_factor = max(min_dimension / width, min_dimension / height)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            image = image.resize((new_width, new_height), Image.LANCZOS)
            logger.info(f"Image resized to: {new_width}x{new_height}")
        
        # Optional: Convert to grayscale (can improve OCR in some cases)
        # Uncomment if needed:
        # from PIL import ImageEnhance
        # image = image.convert('L')
        # enhancer = ImageEnhance.Contrast(image)
        # image = enhancer.enhance(2.0)
        
        return image
    
    except Exception as e:
        logger.warning(f"Error during image preprocessing: {str(e)}")
        # Return original image if preprocessing fails
        return image


def extract_text_with_confidence(image_path):
    """
    Extract text with confidence scores (advanced feature)
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        list: List of dictionaries containing text and confidence scores
    """
    try:
        image = Image.open(image_path)
        processed_image = preprocess_image(image)
        
        # Get detailed OCR data including confidence scores
        ocr_data = pytesseract.image_to_data(
            processed_image,
            output_type=pytesseract.Output.DICT
        )
        
        results = []
        n_boxes = len(ocr_data['text'])
        
        for i in range(n_boxes):
            if int(ocr_data['conf'][i]) > 30:  # Filter low confidence results
                text = ocr_data['text'][i].strip()
                if text:
                    results.append({
                        'text': text,
                        'confidence': int(ocr_data['conf'][i]),
                        'left': ocr_data['left'][i],
                        'top': ocr_data['top'][i],
                        'width': ocr_data['width'][i],
                        'height': ocr_data['height'][i]
                    })
        
        return results
    
    except Exception as e:
        logger.error(f"Error extracting text with confidence: {str(e)}")
        raise


def test_tesseract_installation():
    """
    Test if Tesseract is properly installed and accessible
    
    Returns:
        bool: True if Tesseract is working
    """
    try:
        version = pytesseract.get_tesseract_version()
        logger.info(f"Tesseract version: {version}")
        return True
    except Exception as e:
        logger.error(f"Tesseract installation test failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Test the OCR functionality
    logging.basicConfig(level=logging.INFO)
    
    if test_tesseract_installation():
        print("✓ Tesseract is properly installed and working")
    else:
        print("✗ Tesseract installation test failed")
        print("Please install Tesseract OCR from:")
        print("https://github.com/UB-Mannheim/tesseract/wiki")
