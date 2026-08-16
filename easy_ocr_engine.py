import easyocr
import numpy as np
from PIL import Image
import streamlit as st

@st.cache_resource
def load_ocr_reader():
    # Keep GPU disabled to conserve system memory
    return easyocr.Reader(['en'], gpu=False)

def extract_text_from_image(image: Image.Image) -> list[str]:
    reader = load_ocr_reader()
    
    # Pass image array directly to avoid memory spikes from 3x upscaling
    img_array = np.array(image.convert('RGB'))
    
    # Run EasyOCR
    results = reader.readtext(img_array, detail=0, paragraph=False)
    
    # Filter empty lines
    return [line.strip() for line in results if line.strip()]
