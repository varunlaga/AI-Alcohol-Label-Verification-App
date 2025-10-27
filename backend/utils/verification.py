"""
Verification compares form data with extracted OCR text from label images
"""

import re
import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

# Government warning text that should appear on labels
GOVERNMENT_WARNING_KEYWORDS = [
    "GOVERNMENT WARNING",
    "SURGEON GENERAL",
    "ACCORDING TO THE SURGEON GENERAL",
    "WOMEN SHOULD NOT DRINK",
    "ALCOHOLIC BEVERAGES DURING PREGNANCY",
    "CONSUMPTION OF ALCOHOLIC BEVERAGES",
    "IMPAIRS YOUR ABILITY"
]


def normalize_text(text):
    """
    Normalize text for comparison by removing extra whitespace and converting to lowercase
    
    Args:
        text (str): Input text
        
    Returns:
        str: Normalized text
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Replace multiple whitespaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep alphanumeric, spaces, %, and common punctuation
    text = re.sub(r'[^a-z0-9\s%.\-/]', '', text)
    
    return text.strip()


def fuzzy_match(text1, text2, threshold=0.8):
    """
    Perform fuzzy string matching using sequence matcher
    
    Args:
        text1 (str): First text to compare
        text2 (str): Second text to compare
        threshold (float): Similarity threshold (0.0 to 1.0)
        
    Returns:
        bool: True if texts are similar above threshold
    """
    ratio = SequenceMatcher(None, text1, text2).ratio()
    logger.debug(f"Fuzzy match ratio: {ratio:.2f} for '{text1}' vs '{text2}'")
    return ratio >= threshold


def contains_text(haystack, needle, fuzzy=True, threshold=0.8):
    """
    Check if needle text is contained in haystack with optional fuzzy matching
    
    Args:
        haystack (str): Text to search in
        needle (str): Text to search for
        fuzzy (bool): Use fuzzy matching
        threshold (float): Fuzzy match threshold
        
    Returns:
        bool: True if needle is found in haystack
    """
    haystack_norm = normalize_text(haystack)
    needle_norm = normalize_text(needle)
    
    # Exact substring match
    if needle_norm in haystack_norm:
        logger.debug(f"Exact match found: '{needle}' in text")
        return True
    
    # Fuzzy matching: check if needle matches any portion of haystack
    if fuzzy:
        # Split haystack into words/phrases and check against needle
        words = haystack_norm.split()
        
        # Try matching with consecutive word combinations
        needle_words = needle_norm.split()
        needle_len = len(needle_words)
        
        for i in range(len(words) - needle_len + 1):
            phrase = ' '.join(words[i:i + needle_len])
            if fuzzy_match(phrase, needle_norm, threshold):
                logger.debug(f"Fuzzy match found: '{phrase}' matches '{needle}'")
                return True
    
    return False


def verify_brand_name(form_brand, extracted_text):
    """
    Verify if brand name from form appears in extracted text
    
    Args:
        form_brand (str): Brand name from form
        extracted_text (str): OCR extracted text
        
    Returns:
        dict: Verification result
    """
    logger.info(f"Verifying brand name: {form_brand}")
    
    if contains_text(extracted_text, form_brand, fuzzy=True, threshold=0.85):
        return {
            'field': 'Brand Name',
            'status': 'match',
            'message': f"✓ Brand name '{form_brand}' found on the label."
        }
    else:
        return {
            'field': 'Brand Name',
            'status': 'mismatch',
            'message': f"✗ Brand name '{form_brand}' not found on the label. Please verify the image matches the form data."
        }


def verify_product_type(form_type, extracted_text):
    """
    Verify if product class/type from form appears in extracted text
    
    Args:
        form_type (str): Product type from form
        extracted_text (str): OCR extracted text
        
    Returns:
        dict: Verification result
    """
    logger.info(f"Verifying product type: {form_type}")
    
    # Product types can be long phrases, so use slightly lower threshold
    if contains_text(extracted_text, form_type, fuzzy=True, threshold=0.75):
        return {
            'field': 'Product Class/Type',
            'status': 'match',
            'message': f"✓ Product type '{form_type}' found on the label."
        }
    else:
        # Try matching individual words for partial matches
        words = form_type.lower().split()
        if len(words) > 2:
            # Check if at least the key words are present
            key_words_found = sum(1 for word in words if len(word) > 3 and word in normalize_text(extracted_text))
            if key_words_found >= len(words) // 2:
                return {
                    'field': 'Product Class/Type',
                    'status': 'match',
                    'message': f"✓ Product type '{form_type}' found on the label (partial match)."
                }
        
        return {
            'field': 'Product Class/Type',
            'status': 'mismatch',
            'message': f"✗ Product type '{form_type}' not found on the label."
        }


def verify_alcohol_content(form_abv, extracted_text):
    """
    Verify if alcohol content from form appears in extracted text
    
    Args:
        form_abv (str): Alcohol content from form (as string)
        extracted_text (str): OCR extracted text
        
    Returns:
        dict: Verification result
    """
    logger.info(f"Verifying alcohol content: {form_abv}%")
    
    try:
        # Convert form ABV to float
        form_abv_float = float(form_abv)
        
        # Find all percentage patterns in extracted text
        # Patterns: "45%", "45 %", "45.0%", "45% ABV", "ABV 45%", "Alc. 45% Vol."
        percentage_patterns = [
            r'(\d+\.?\d*)\s*%',  # Basic percentage
            r'(\d+\.?\d*)\s*percent',  # Written as "percent"
            r'abv[:\s]*(\d+\.?\d*)',  # ABV: 45 or ABV 45
            r'alcohol[:\s]*(\d+\.?\d*)',  # Alcohol: 45
            r'alc[.:\s]*(\d+\.?\d*)',  # Alc. 45 or Alc: 45
        ]
        
        found_percentages = []
        text_lower = extracted_text.lower()
        
        for pattern in percentage_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                try:
                    percentage = float(match)
                    if 0 <= percentage <= 100:  # Valid percentage range
                        found_percentages.append(percentage)
                except ValueError:
                    continue
        
        # Remove duplicates
        found_percentages = list(set(found_percentages))
        logger.debug(f"Found percentages in text: {found_percentages}")
        
        # Check if form ABV matches any found percentage (with tolerance)
        tolerance = 0.5  # Allow 0.5% difference
        for found_abv in found_percentages:
            if abs(form_abv_float - found_abv) <= tolerance:
                return {
                    'field': 'Alcohol Content',
                    'status': 'match',
                    'message': f"✓ Alcohol content {form_abv}% found on the label."
                }
        
        # If percentages found but don't match
        if found_percentages:
            return {
                'field': 'Alcohol Content',
                'status': 'mismatch',
                'message': f"✗ Expected {form_abv}% but found {found_percentages[0]}% on the label."
            }
        else:
            return {
                'field': 'Alcohol Content',
                'status': 'not_found',
                'message': f"⚠ Could not find alcohol content on the label. Expected {form_abv}%."
            }
    
    except ValueError:
        logger.error(f"Invalid ABV value: {form_abv}")
        return {
            'field': 'Alcohol Content',
            'status': 'not_found',
            'message': f"⚠ Invalid alcohol content format in form."
        }


def verify_net_contents(form_contents, extracted_text):
    """
    Verify if net contents from form appears in extracted text
    
    Args:
        form_contents (str): Net contents from form
        extracted_text (str): OCR extracted text
        
    Returns:
        dict: Verification result or None if not provided
    """
    if not form_contents:
        return None
    
    logger.info(f"Verifying net contents: {form_contents}")
    
    # Normalize the form contents (like "750ml", "750 ml", "750 mL" should all match)
    form_normalized = normalize_text(form_contents)
    
    # Extract volume patterns from text
    # Patterns: "750ml", "750 ml", "750mL", "12 fl oz", "1L", "1 liter"
    volume_patterns = [
        r'(\d+\.?\d*)\s*(ml|milliliter|millilitre)',
        r'(\d+\.?\d*)\s*(l|liter|litre)',
        r'(\d+\.?\d*)\s*(oz|ounce)',
        r'(\d+\.?\d*)\s*(fl\s*oz|fluid\s*ounce)',
        r'(\d+\.?\d*)\s*(cl|centiliter)',
    ]
    
    text_lower = extracted_text.lower()
    
    # Check for direct match first
    if form_normalized in normalize_text(extracted_text):
        return {
            'field': 'Net Contents',
            'status': 'match',
            'message': f"✓ Net contents '{form_contents}' found on the label."
        }
    
    # Extract number and unit from form input
    form_match = re.search(r'(\d+\.?\d*)\s*([a-z]+)', form_normalized)
    if form_match:
        form_num = float(form_match.group(1))
        form_unit = form_match.group(2)
        
        # Search for similar volume in text
        for pattern in volume_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                try:
                    found_num = float(match[0])
                    found_unit = match[1].replace(' ', '')
                    
                    # Check if units match (with variations)
                    units_match = (
                        form_unit == found_unit or
                        form_unit in found_unit or
                        found_unit in form_unit
                    )
                    
                    if units_match and abs(form_num - found_num) < 1:
                        return {
                            'field': 'Net Contents',
                            'status': 'match',
                            'message': f"✓ Net contents '{form_contents}' found on the label."
                        }
                except ValueError:
                    continue
    
    return {
        'field': 'Net Contents',
        'status': 'not_found',
        'message': f"⚠ Net contents '{form_contents}' not clearly found on the label."
    }


def verify_government_warning(extracted_text):
    """
    Verify if government warning text appears on the label
    
    Args:
        extracted_text (str): OCR extracted text
        
    Returns:
        dict: Verification result
    """
    logger.info("Verifying government warning")
    
    text_upper = extracted_text.upper()
    
    # Check for main warning phrase
    if "GOVERNMENT WARNING" in text_upper:
        # Check for additional warning keywords
        keyword_count = sum(1 for keyword in GOVERNMENT_WARNING_KEYWORDS if keyword in text_upper)
        
        if keyword_count >= 2:
            return {
                'field': 'Government Warning',
                'status': 'match',
                'message': "✓ Government warning statement found on the label."
            }
        else:
            return {
                'field': 'Government Warning',
                'status': 'warning',
                'message': "⚠ 'GOVERNMENT WARNING' found but complete warning text may be incomplete."
            }
    else:
        return {
            'field': 'Government Warning',
            'status': 'not_found',
            'message': "✗ Government warning statement not found on the label. This is required by law."
        }


def verify_label_data(form_data, extracted_text):
    """
    Main verification function that compares all form data with extracted text
    
    Args:
        form_data (dict): Dictionary containing form fields
        extracted_text (str): OCR extracted text from label
        
    Returns:
        list: List of verification results for each field
    """
    logger.info("Starting label verification")
    logger.debug(f"Form data: {form_data}")
    logger.debug(f"Extracted text length: {len(extracted_text)} characters")
    
    results = []
    
    # Verify Brand Name
    if form_data.get('brand_name'):
        results.append(verify_brand_name(form_data['brand_name'], extracted_text))
    
    # Verify Product Type
    if form_data.get('product_type'):
        results.append(verify_product_type(form_data['product_type'], extracted_text))
    
    # Verify Alcohol Content
    if form_data.get('alcohol_content'):
        results.append(verify_alcohol_content(form_data['alcohol_content'], extracted_text))
    
    # Verify Net Contents (optional)
    net_contents_result = verify_net_contents(form_data.get('net_contents'), extracted_text)
    if net_contents_result:
        results.append(net_contents_result)
    
    # Verify Government Warning (bonus feature)
    results.append(verify_government_warning(extracted_text))
    
    logger.info(f"Verification completed. {len(results)} checks performed.")
    
    return results


if __name__ == "__main__":
    # Test the verification functions
    logging.basicConfig(level=logging.DEBUG)
    
    # Sample test
    test_text = """
    OLD TOM DISTILLERY
    Kentucky Straight Bourbon Whiskey
    45% Alc./Vol. (90 Proof)
    750 mL
    
    GOVERNMENT WARNING: (1) According to the Surgeon General, 
    women should not drink alcoholic beverages during pregnancy 
    because of the risk of birth defects. (2) Consumption of 
    alcoholic beverages impairs your ability to drive a car or 
    operate machinery, and may cause health problems.
    """
    
    test_form = {
        'brand_name': 'Old Tom Distillery',
        'product_type': 'Kentucky Straight Bourbon Whiskey',
        'alcohol_content': '45',
        'net_contents': '750 mL'
    }
    
    results = verify_label_data(test_form, test_text)
    
    print("\n=== Verification Results ===")
    for result in results:
        print(f"{result['field']}: {result['status']} - {result['message']}")
