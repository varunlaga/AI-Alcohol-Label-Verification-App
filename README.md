# AI-Alcohol-Label-Verification-App

About: This is an AI-powered alcohol label verification app for Alcohol and Tobacco Tax and Trade Bureau (TTB) compliance checking.

# Live


# Features

- Form Input: Simplified TTB application form with key fields
- Image Upload: Support for JPEG/PNG with drag-and-drop
- OCR Processing: Tesseract-based text extraction from label images
- Smart Verification: Fuzzy matching with text normalization
- Comprehensive Checks:
  - Brand Name verification (85% similarity threshold)
  - Product Class/Type verification (75% similarity threshold)
  - Alcohol Content verification (multiple pattern recognition)
  - Net Contents verification (volume pattern matching)
  - Government Warning detection (bonus feature)
- Clear Results: Field-by-field verification with detailed feedback
- Error Handling: Error handling of OCR failures and mismatches

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
