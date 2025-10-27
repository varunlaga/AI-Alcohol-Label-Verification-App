# AI-Alcohol-Label-Verification-App

About: This is an AI-powered full-stack web application designed to simulate the Alcohol and Tobacco Tax and Trade Bureau ($\text{TTB}$) label approval process. It verifies that the information submitted in a simplified $\text{TTB}$ application form (Brand Name, $\text{ABV}$, and etc.) accurately matches the text content extracted from the uploaded alcohol beverage label image. The application uses Tesseract OCR for text extraction and implements verification algorithms using fuzzy string matching and regular expressions to determine compliance status for each field.

## Live Application

Link: 

## Key Features

- Form Input: Simplified TTB application form with mandatory and optional key fields
- Image Upload: Support for JPEG/PNG with a user-friendly drag and drop interface
- OCR Processing: Tesseract-based text extraction from label images
- Different Verifications: Fuzzy matching with text normalization (normalize_text function) to account for slight $\text{OCR}$ (Optical Character Recognition) errors and formatting differences
- Comprehensive Verification Checks:
  - Brand Name Verification (85% similarity threshold for fuzzy matching)
  - Product Class/Type Verification (75% similarity threshold for fuzzy matching)
  - Alcohol Content Verification (Multiple pattern recognition (e.g., 45% $\text{Alc.}$/Vol.") and numerical comparison)
  - Net Contents Verification (Volume pattern matching (e.g., "750 $\text{mL}$", "12 fl oz"))
  - Government Warning Detection ($\text{Bonus}$ feature to check for mandatory health warning keywords)
- Clear Results: Field-by-field verification status with detailed feedback on match/mismatch/warning
- Error Handling: Graceful handling of $\text{OCR}$ failures, image upload errors, and data mismatches

## Tech Stack

    | Component        | Technology     | Version/Tool                    |
    |------------------|----------------|---------------------------------|
    | Backend Framework| Flask          | Flask 3.0.0                     |
    | OCR Engine       | Tesseract OCR  | pytesseract lib                 |
    | Image Processing | PIL            | Pillow                          |
    | Language         | Python         | Python 3.11.0                   |
    | Frontend         | HTML, CSS, JS  | HTML5, CSS3, Vanilla JavaScript | 

## How to Run Locally







## Configuration and Environment Variables







## Design & Approach Documentation

# OCR Tool Selection

Tool Used: Tesseract OCR via pytesseract library

Justification: Tesseract was chosen because it is open-source, free, and can be run locally on the deployment server for Linux deployments like Render. This avoids the complexity and cost of external cloud API keys for the core Minimum Viable Product (MVP).

# Text Normalization (normalize_text)

The core function for successful verification is normalize_text in verification.py.

Approach: All text (both form input and OCR output) is converted to lowercase and stripped of most special characters (except $\text{.}$ / $\text{-}$ / %) to create a clean, comparable string.

Purpose: This mitigates the common issue of OCR introducing small errors (e.g., misreading O for 0, capitalizing randomly, or adding extra spaces) and ensures the comparison is focused on content not overly strict formatting.

# Key Assumptions and Limitations

    | Category           | Assumption/Limitation | Impact                          |
    |--------------------|-----------------------|---------------------------------|
    | Image Quality      | Flask          | Flask 3.0.0                     |
    | Language           | Tesseract OCR  | pytesseract lib                 |
    | Verification Logic | PIL            | Pillow                          |
    | Language         | Python         | Python 3.11.0                   |
    | Frontend         | HTML, CSS, JS  | HTML5, CSS3, Vanilla JavaScript | 










