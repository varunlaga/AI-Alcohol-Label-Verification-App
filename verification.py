import re

def verify_label_compliance(extracted_text: list[str]) -> dict:
    """
    Evaluates extracted label text against required regulatory rules.
    """
    full_text = " ".join(extracted_text)
    full_text_lower = full_text.lower()
    
    # Rule 1: Brand Name / Identity Check
    has_brand = len(extracted_text) > 0
    
    # Rule 2: Government Warning / Health Caution
    has_warning = "government warning" in full_text_lower or "warning" in full_text_lower
    
    # Rule 3: Alcohol By Volume (ABV) Detection
    abv_pattern = re.compile(r'(\d+(\.\d+)?)\s*%\s*(alc|alc/vol|alcohol)?', re.IGNORECASE)
    abv_match = abv_pattern.search(full_text)
    abv_value = abv_match.group(0) if abv_match else "Not Found"
    
    # Rule 4: Net Contents Volume (e.g., 750ml, 1L)
    volume_pattern = re.compile(r'\b\d+\s*(ml|l|liter|liters|fl oz)\b', re.IGNORECASE)
    vol_match = volume_pattern.search(full_text)
    volume_value = vol_match.group(0) if vol_match else "Not Found"

    # Overall Compliance Determination
    is_compliant = has_brand and has_warning and (abv_value != "Not Found") and (volume_value != "Not Found")
    
    return {
        "is_compliant": is_compliant,
        "checks": {
            "Brand / Text Detected": has_brand,
            "Government Warning": has_warning,
            "ABV Stated": abv_value != "Not Found",
            "Net Volume Stated": volume_value != "Not Found"
        },
        "extracted_details": {
            "ABV": abv_value,
            "Volume": volume_value,
            "Raw Text": extracted_text
        }
    }