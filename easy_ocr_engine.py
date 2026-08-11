import easyocr
import numpy as np
from PIL import Image
import streamlit as st

@st.cache_resource
def load_ocr_reader():
    """Cache the EasyOCR reader so model weights load only once."""
    return easyocr.Reader(['en'], gpu=False)

def extract_text_from_image(image: Image.Image) -> list[str]:
    """
    Processes an uploaded PIL image and returns extracted text lines.
    """
    reader = load_ocr_reader()
    img_array = np.array(image)
    
    # Extract text with EasyOCR
    results = reader.readtext(img_array)
    
    # Extract text content from bounding boxes
    extracted_lines = [text for (_, text, confidence) in results if confidence > 0.2]
    return extracted_lines