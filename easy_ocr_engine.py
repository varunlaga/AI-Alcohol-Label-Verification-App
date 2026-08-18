import os
import cv2
import easyocr
import numpy as np
from PIL import Image
import streamlit as st

@st.cache_resource
def load_ocr_reader():
    """
    Caches the EasyOCR Reader instance across user sessions
    to prevent re-downloading model weights or hitting RAM limits.
    """
    # Create model cache folder
    model_dir = os.path.join(os.path.expanduser("~"), ".EasyOCR", "model")
    os.makedirs(model_dir, exist_ok=True)
    
    return easyocr.Reader(
        ['en'], 
        gpu=False, 
        model_storage_directory=model_dir,
        download_enabled=True
    )

def preprocess_image_generalized(image: Image.Image) -> np.ndarray:
    """
    Generalized pre-processing to clarify text on blurry, dark, 
    or low-resolution labels without high RAM overhead.
    """
    img_gray = np.array(image.convert('L'))
    h, w = img_gray.shape
    
    # Dynamic Upscaling: Only upscale if image resolution is low
    if min(h, w) < 800:
        scale = 800.0 / min(h, w)
        img_gray = cv2.resize(img_gray, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    
    # Contrast Limited Adaptive Histogram Equalization (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(img_gray)
    
    # Light Unsharp Mask (Sharpening edges of blurry characters)
    blurred = cv2.GaussianBlur(enhanced, (0, 0), 3)
    sharpened = cv2.addWeighted(enhanced, 1.5, blurred, -0.5, 0)
    
    return cv2.cvtColor(sharpened, cv2.COLOR_GRAY2RGB)

def extract_text_from_image(image: Image.Image) -> list[str]:
    reader = load_ocr_reader()
    processed_img = preprocess_image_generalized(image)
    results = reader.readtext(processed_img, detail=0)
    return results