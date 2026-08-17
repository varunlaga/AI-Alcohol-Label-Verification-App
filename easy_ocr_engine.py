import cv2
import easyocr
import numpy as np
from PIL import Image
import streamlit as st

@st.cache_resource
def load_ocr_reader():
    return easyocr.Reader(['en'], gpu=False)

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
    # Enhances local contrast to make faint/small text pop out from background colors
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(img_gray)
    
    # Light Unsharp Mask (Sharpening edges of blurry characters)
    blurred = cv2.GaussianBlur(enhanced, (0, 0), 3)
    sharpened = cv2.addWeighted(enhanced, 1.5, blurred, -0.5, 0)
    
    return cv2.cvtColor(sharpened, cv2.COLOR_GRAY2RGB)

def extract_text_from_image(image: Image.Image) -> list[str]:
    reader = load_ocr_reader()
    processed_img = preprocess_image_generalized(image)
    
    # Tuned detection parameters to catch small fine-print text without dropping bounding boxes
    results = reader.readtext(
        processed_img, 
        detail=0, 
        paragraph=False,
        low_text=0.3,       # Detects faint text
        text_threshold=0.4  # Prevents dropping low-confidence characters
    )
    
    return [line.strip() for line in results if line.strip()]