import easyocr
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import streamlit as st

@st.cache_resource
def load_ocr_reader():
    """Cache the EasyOCR reader so model weights load only once."""
    return easyocr.Reader(['en'], gpu=False)

def extract_text_from_image(image: Image.Image) -> list[str]:
    """
    Applies image preprocessing tailored for low-res labels to ensure 
    small fine print like Government Warnings get extracted.
    """
    reader = load_ocr_reader()
    extracted_lines = []
    
    # Pass 1: Upscale & Sharpen Original Image
    w, h = image.size
    upscaled = image.resize((w * 3, h * 3), Image.Resampling.LANCZOS)
    
    # Mild contrast and sharpening
    enhancer = ImageEnhance.Contrast(upscaled)
    sharpened = enhancer.enhance(1.4).filter(ImageFilter.SHARPEN)
    
    results_pass1 = reader.readtext(np.array(sharpened))
    for (_, text, conf) in results_pass1:
        if conf > 0.05:
            extracted_lines.append(text)
            
    # Pass 2: Grayscale thresholding for small dense text
    gray = upscaled.convert('L')
    enhancer_gray = ImageEnhance.Contrast(gray)
    high_contrast_gray = enhancer_gray.enhance(1.8)
    
    results_pass2 = reader.readtext(np.array(high_contrast_gray))
    for (_, text, conf) in results_pass2:
        if conf > 0.05 and text not in extracted_lines:
            extracted_lines.append(text)
            
    return extracted_lines