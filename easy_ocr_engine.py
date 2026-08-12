import easyocr
import numpy as np
from PIL import Image, ImageEnhance
import streamlit as st

@st.cache_resource
def load_ocr_reader():
    """Cache the EasyOCR reader so model weights load only once."""
    return easyocr.Reader(['en'], gpu=False)

def extract_text_from_image(image: Image.Image) -> list[str]:
    """
    Runs a dual-pass extraction (Original + Preprocessed) to ensure both large text
    and fine print are captured reliably.
    """
    reader = load_ocr_reader()
    extracted_lines = []
    
    # --- Pass 1: Original Image ---
    orig_array = np.array(image.convert('RGB'))
    results_orig = reader.readtext(orig_array)
    for (_, text, conf) in results_orig:
        if conf > 0.1 and text not in extracted_lines:
            extracted_lines.append(text)
            
    # --- Pass 2: Grayscale + Upscaled + High Contrast (for Fine Print) ---
    gray_img = image.convert('L')
    w, h = gray_img.size
    # Upscale 2.5x to help OCR read small government warnings and volume text
    gray_img = gray_img.resize((int(w * 2.5), int(h * 2.5)), Image.Resampling.LANCZOS)
    
    # Increase contrast
    enhancer = ImageEnhance.Contrast(gray_img)
    enhanced_img = enhancer.enhance(2.5)
    
    proc_array = np.array(enhanced_img)
    results_proc = reader.readtext(proc_array)
    
    for (_, text, conf) in results_proc:
        # Avoid duplicate entries while pulling in missing lines
        if conf > 0.08 and text not in extracted_lines:
            extracted_lines.append(text)
            
    return extracted_lines