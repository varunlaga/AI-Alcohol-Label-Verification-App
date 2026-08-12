import re

def verify_label_compliance(extracted_text: list[str], form_data: dict = None) -> dict:
    """
    Evaluates extracted label text against regulatory rules and form inputs.
    """
    full_text = " ".join(extracted_text)
    full_text_lower = full_text.lower()
    
    # 1. Text Detected Check
    has_text = len(extracted_text) > 0
    
    # 2. Government Warning Check (Handles "GOVERNMENT WARNING:", extra spaces, etc.)
    has_warning = bool(re.search(r'government\s*warning', full_text_lower))
    
    # 3. ABV Detection (Handles "40.0 % alc./vol.", "40.0%", "40% alc/vol")
    abv_pattern = re.compile(r'(\d+(\.\d+)?)\s*%\s*(alc|alc/vol|alc\./vol\.|alcohol|proof)?', re.IGNORECASE)
    abv_match = abv_pattern.search(full_text)
    abv_value = abv_match.group(0) if abv_match else "Not Found"
    
    # 4. Net Contents Volume (Handles "750 mL", "750ml", "1 L", "12 fl oz")
    volume_pattern = re.compile(r'\b\d+(\.\d+)?\s*(ml|l|liter|liters|fl\s*oz)\b', re.IGNORECASE)
    vol_match = volume_pattern.search(full_text)
    volume_value = vol_match.group(0) if vol_match else "Not Found"

    # 5. Form Field Matching
    brand_match = True
    if form_data and form_data.get("brand"):
        user_brand = form_data["brand"].strip().lower()
        if len(user_brand) >= 4:
            # Check if entered brand exists anywhere in the OCR text
            brand_match = user_brand in full_text_lower

    # Overall Compliance
    is_compliant = has_text and has_warning and (abv_value != "Not Found") and (volume_value != "Not Found") and brand_match
    
    return {
        "is_compliant": is_compliant,
        "checks": {
            "Text / Brand Detected": has_text,
            "Government Warning": has_warning,
            "ABV Stated": abv_value != "Not Found",
            "Net Volume Stated": volume_value != "Not Found",
            "Brand Matches Form": brand_match
        },
        "extracted_details": {
            "ABV Found": abv_value,
            "Volume Found": volume_value,
            "Raw Text Lines": extracted_text
        }
    }