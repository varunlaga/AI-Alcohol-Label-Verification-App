import easyocr
import numpy as np
from PIL import Image, ImageEnhance, ImageOps
import streamlit as st

@st.cache_resource
def load_ocr_reader():
    return easyocr.Reader(['en'], gpu=False)

def extract_text_from_image(image: Image.Image) -> list[str]:
    reader = load_ocr_reader()
    
    # 1. Upscale 2x for clarity
    w, h = image.size
    scaled = image.resize((w * 2, h * 2), Image.Resampling.LANCZOS)
    
    # 2. Convert to Grayscale & Enhances Contrast
    gray = ImageOps.autocontrast(scaled.convert('L'))
    enhancer = ImageEnhance.Contrast(gray)
    enhanced = enhancer.enhance(1.5)
    
    # 3. Single OCR pass with clean string outputs
    results = reader.readtext(np.array(enhanced), detail=0, paragraph=False)
    
    # Clean whitespace and drop empty lines
    extracted_lines = [text.strip() for text in results if text.strip()]
    return extracted_lines