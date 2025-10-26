# AI-Alcohol-Label-Verification-App

About: This is an AI-powered full-stack web application designed to simulate the Alcohol and Tobacco Tax and Trade Bureau ($\text{TTB}$) label approval process. It verifies that the information submitted in a simplified $\text{TTB}$ application form (Brand Name, $\text{ABV}$, and etc.) accurately matches the text content extracted from the uploaded alcohol beverage label image.The application uses Tesseract OCR for text extraction and implements verification algorithms using fuzzy string matching and regular expressions to determine compliance status for each field.

# Live Application

Link: 

# Key Features

- Form Input: Simplified TTB application form with mandatory and optional key fields
- Image Upload: Support for JPEG/PNG with a user-friendly drag and drop interface
- OCR Processing: Tesseract-based text extraction from label images
- Different Verifications: Fuzzy matching with text normalization (normalize_text function) to account for slight $\text{OCR}$ errors and formatting differences
- Comprehensive Verification Checks:
  - Brand Name Verification (85% similarity threshold for fuzzy matching)
  - Product Class/Type Verification (75% similarity threshold for fuzzy matching)
  - Alcohol Content Verification (Multiple pattern recognition (e.g., "$\text{45\%}$ $\text{Alc.}$/Vol.", "90 Proof") and numerical comparison)
  - Net Contents Verification (Volume pattern matching (e.g., "750 $\text{mL}$", "12 fl oz"))
  - Government Warning Detection ($\text{Bonus}$ feature to check for mandatory health warning keywords)
- Clear Results: Field-by-field verification status with detailed feedback on match/mismatch/warning
- Error Handling: Graceful handling of $\text{OCR}$ failures, image upload errors, and data mismatches.

## Tech Stack

### Backend

- Framework: Flask 3.0.0
- OCR Engine: Tesseract OCR via pytesseract
- Image Processing: Python Image Family (PIL)
- Language: Python 3.11

### Frontend

- HTML5
- CSS3
- Vanilla JavaScript
