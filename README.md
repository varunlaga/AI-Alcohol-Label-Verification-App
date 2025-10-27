# AI-Alcohol-Label-Verification-App

About: This is an AI-powered full-stack web application designed to simulate the Alcohol and Tobacco Tax and Trade Bureau ($\text{TTB}$) label approval process. It verifies that the information submitted in a simplified $\text{TTB}$ application form (Brand Name, $\text{ABV}$, and etc.) accurately matches the text content extracted from the uploaded alcohol beverage label image. The application uses Tesseract OCR for text extraction and implements verification algorithms using fuzzy string matching and regular expressions to determine compliance status for each field.

## Live Application using Render

Link: 

## Key Features

- Form Input: Simplified TTB application form with mandatory and optional key fields
- Image Upload: Support for JPEG/PNG with a user-friendly drag and drop interface
- OCR Processing: Tesseract-based text extraction from label images
- Different Verifications: Fuzzy matching with text normalization (normalize_text function) to account for slight $\text{OCR}$ (Optical Character Recognition) errors and formatting differences
- Comprehensive Verification Checks:
  - Brand Name Verification (85% similarity threshold for fuzzy matching)
  - Product Class/Type Verification (75% similarity threshold for fuzzy matching)
  - Alcohol Content Verification (Multiple pattern recognition (like 45% $\text{Alc.}$/Vol.) and numerical comparison)
  - Net Contents Verification (Volume pattern matching (like 750 $\text{mL}$, 12 fl oz, 1 L))
  - Government Warning Detection (Bonus feature to check for mandatory health warning keywords)
- Clear Results: Field-by-field verification status with detailed feedback on match/mismatch/warning
- Error Handling: Graceful handling of $\text{OCR}$ failures, image upload errors, and data mismatches

## Tech Stack

|                  Component                 |          Technology          |           Version/Tool          |   
|--------------------------------------------|------------------------------|---------------------------------|
|              Backend Framework             |             Flask            |              3.0.0              |
| OCR (Optical Character Recognition) Engine |         Tesseract OCR        |       pytesseract library       |
|              Image Processing              | PIL (Python Imaging Library) |              Pillow             |
|                  Language                  |            Python            |              3.11.0             |
|             Frontend Framework             |         HTML, CSS, JS        | HTML5, CSS3, Vanilla JavaScript |


## How to Run Locally

Below are the steps to set up and run the app locally.

### Prerequisites

Must have installed:

- Python 3.11.0
- Tesseract OCR

### Setup the Environment

#### Clone the repository

- git clone https://github.com/varunlaga/AI-Alcohol-Label-Verification-App.git
- cd AI-Alcohol-Label-Verification-App

#### Create and activate a Python virtual environment

- python -m venv my_venv
- source my_env/Scripts/activate

#### Installation

Install the required Python dependencies

- pip install -r requirements.txt

#### Run the Application

Set environment variables (optional but recommended)

- export FLASK_ENV=development
- export FLASK_APP=backend/app.py

Start the Flask server

- python backend/app.py

The application should now be running and accessible in the web browser: http://localhost:5000

## Configuration and Environment Variables







## Design & Approach Documentation

### OCR Tool Selection

Tool Used: Tesseract OCR via pytesseract library

Justification: Tesseract was chosen because it is open-source, free, and can be run locally on the deployment server for Linux deployments like Render. This avoids the complexity and cost of external cloud API keys for the core Minimum Viable Product (MVP).

### Text Normalization (normalize_text)

The core function for successful verification is normalize_text in verification.py.

Approach: All text (both form input and OCR output) is converted to lowercase and stripped of most special characters (except $\text{.}$ / $\text{-}$ / %) to create a clean, comparable string.

Purpose: This mitigates the common issue of OCR introducing small errors (like misreading O for 0, capitalizing randomly, or adding extra spaces) and ensures the comparison is focused on content not overly strict formatting.

### Key Assumptions and Limitations

|      Category      |                                                    Assumption / Limitation                                                   |                                                         Impact                                                         |   
|:------------------:|:----------------------------------------------------------------------------------------------------------------------------:|:----------------------------------------------------------------------------------------------------------------------:|
|    Image Quality   |                   Assumes the uploaded label image is clear, well-lit, and not heavily distorted or rotated                  |                  Poor quality images will severely degrade OCR accuracy and lead to "mismatch" results                 |  
|      Language      |    Assumes only English text and Tesseract uses English as default so it must be configured for other languages if needed    |                         Non-English characters or complex scripts may not be reliably extracted                        |   
| Verification Logic | Assumes verification is based purely on the presence of text so does not verify the location or context of the text on label | The system can not determine if a mandatory statement is in the required font size or location only if the text exists |   
|  ABV/Net Contents  |   Assumes verification relies on successful extraction of specific numerical patterns like 45% or unit formats like 750 mL   |        Unusual typography on the label may prevent the regex from matching the content even if OCR extracts text       |   








