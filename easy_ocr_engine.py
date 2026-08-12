import cv2
import easyocr
import numpy as np
from PIL import Image
import streamlit as st

@st.cache_resource
def load_ocr_reader():
    return easyocr.Reader(['en'], gpu=False)

def preprocess_for_ocr(pil_image: Image.Image) -> np.ndarray:
    """
    Applies OpenCV adaptive thresholding and upscaling to handle 
    low-resolution label images and fine print.
    """
    # Convert PIL Image to OpenCV BGR format
    open_cv_image = np.array(pil_image.convert('RGB'))
    img_bgr = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)
    
    # Grayscale conversion
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    
    # 3x Upscaling with cubic interpolation
    h, w = gray.shape
    resized = cv2.resize(gray, (w * 3, h * 3), interpolation=cv2.INTER_CUBIC)
    
    # Denoise & Adaptive Thresholding
    blurred = cv2.GaussianBlur(resized, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    return thresh

def extract_text_from_image(image: Image.Image) -> list[str]:
    reader = load_ocr_reader()
    
    # Process both original grayscale and thresholded images to maximize accuracy
    processed_img = preprocess_for_ocr(image)
    
    # EasyOCR execution with paragraph mode off for fine-grained line extraction
    results = reader.readtext(processed_img, detail=0, paragraph=False)
    
    # Filter out empty or whitespace-only lines
    extracted_lines = [line.strip() for line in results if line.strip()]
    return extracted_lines