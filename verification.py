import re

def verify_label_compliance(extracted_text: list[str], form_data: dict = None) -> dict:
    """
    Evaluates extracted label text against regulatory requirements and verifies 
    that form input values strictly match the extracted OCR data.
    """
    full_text = " ".join(extracted_text)
    full_text_lower = full_text.lower()
    
    # Government Warning Detection (flexible to handle OCR typos like "GOWERNMENT" or "WARNING:")
    warning_pattern = re.compile(r'(government|gov|gowernment)\s*(warning|warnlng|wamning)', re.IGNORECASE)
    has_warning = bool(warning_pattern.search(full_text_lower)) or "surgeon general" in full_text_lower
    
    # Extract Numerical Values from OCR
    abv_match = re.search(r'(\d+(\.\d+)?)', full_text)
    extracted_abv = float(abv_match.group(1)) if abv_match else None
    
    vol_match = re.search(r'(\d+)\s*(ml|l|fl\s*oz)?', full_text_lower)
    extracted_vol = vol_match.group(1) if vol_match else None

    # Initialize Compliance Flags
    abv_matches_form = False
    vol_matches_form = False
    brand_matches_form = False
    class_matches_form = False

    if form_data:
        # Form ABV Match Check
        user_abv = form_data.get("abv")
        if user_abv is not None and extracted_abv is not None:
            abv_matches_form = abs(float(user_abv) - extracted_abv) < 0.1

        # Form Net Contents Match Check
        user_vol = str(form_data.get("net_contents", "")).strip()
        if user_vol and extracted_vol:
            # Extract digits only for exact comparison (e.g., "700" vs "750")
            user_digits = re.sub(r'\D', '', user_vol)
            vol_matches_form = (user_digits == extracted_vol)

        # Form Brand Match Check
        user_brand = str(form_data.get("brand", "")).strip().lower()
        if user_brand:
            brand_matches_form = user_brand in full_text_lower

        # Form Product Class/Type Match Check
        user_class = str(form_data.get("class", "")).strip().lower()
        if user_class:
            class_matches_form = user_class in full_text_lower

    # Overall Compliance Determination
    is_compliant = (
        has_warning and 
        abv_matches_form and 
        vol_matches_form and 
        brand_matches_form and 
        class_matches_form
    )

    return {
        "is_compliant": is_compliant,
        "checks": {
            "Government Warning Present": has_warning,
            "Brand Matches Form": brand_matches_form,
            "Product Class Matches Form": class_matches_form,
            "ABV Matches Form": abv_matches_form,
            "Net Volume Matches Form": vol_matches_form
        },
        "extracted_details": {
            "Extracted ABV": f"{extracted_abv}%" if extracted_abv else "Not Found",
            "Extracted Volume": f"{extracted_vol} mL" if extracted_vol else "Not Found",
            "Raw Text Lines": extracted_text
        }
    }