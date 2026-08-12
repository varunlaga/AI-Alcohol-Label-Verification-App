import easyocr
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import streamlit as st

@st.cache_resource
def load_ocr_reader():
    return easyocr.Reader(['en'], gpu=False)

def extract_text_from_image(image: Image.Image) -> list[str]:
    reader = load_ocr_reader()
    extracted_lines = []
    
    # Base 3x Upscaling
    w, h = image.size
    scaled = image.resize((w * 3, h * 3), Image.Resampling.LANCZOS)
    
    # Image Pass 1: Sharpened RGB (Good for large colored text)
    pass1 = ImageEnhance.Sharpness(scaled).enhance(2.0)
    
    # Image Pass 2: Grayscale + Autocontrast (Good for medium text)
    pass2 = ImageOps.autocontrast(scaled.convert('L'))
    
    # Image Pass 3: High Contrast Binary Threshold (Good for tiny/blurry fine print)
    pass3 = ImageEnhance.Contrast(pass2).enhance(3.0)
    
    passes = [pass1, pass2, pass3]
    
    for img_pass in passes:
        results = reader.readtext(np.array(img_pass))
        for (_, text, conf) in results:
            clean_text = text.strip()
            # Lower confidence floor (0.02) to capture small warning text
            if conf > 0.02 and clean_text and clean_text not in extracted_lines:
                extracted_lines.append(clean_text)
                
    return extracted_lines