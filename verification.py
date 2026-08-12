import re

def verify_label_compliance(extracted_text: list[str], form_data: dict = None) -> dict:
    """
    Evaluates extracted label text against regulatory requirements and verifies 
    that form input values strictly match the extracted OCR data.
    """
    full_text = " ".join(extracted_text)
    full_text_lower = full_text.lower()
    
    # 1. Flexible Government Warning Check (Handles typos like "GOWERNMENT", "WARNlNG", or missing colons)
    warning_pattern = re.compile(r'(government|gov|gowernment|go\w+ment)\s*(warning|warn\w+|wamning)', re.IGNORECASE)
    has_warning = bool(warning_pattern.search(full_text_lower)) or "surgeon general" in full_text_lower
    
    # 2. Extract ABV (looks for percentage patterns specifically)
    abv_match = re.search(r'(\d+(\.\d+)?)\s*(%|\bpercent\b|\balc\b)', full_text_lower)
    extracted_abv = float(abv_match.group(1)) if abv_match else None
    
    # 3. Extract Volume (specifically looks for numbers tied to volume units or after "Contents")
    extracted_vol = None
    vol_match = re.search(r'(net\s*contents?|contents?)?\s*(\d+)\s*(ml|l|fl\s*oz)\b', full_text_lower)
    if vol_match:
        extracted_vol = vol_match.group(2)
    else:
        # Fallback: find 3-digit standalone numbers like 750 (excluding the ABV number)
        all_nums = re.findall(r'\b\d{3}\b', full_text)
        if all_nums:
            extracted_vol = all_nums[0]

    # Initialize Verification Flags
    abv_matches_form = False
    vol_matches_form = False
    brand_matches_form = False
    class_matches_form = False

    if form_data:
        # Check ABV
        user_abv = form_data.get("abv")
        if user_abv is not None and extracted_abv is not None:
            abv_matches_form = abs(float(user_abv) - extracted_abv) < 0.2

        # Check Volume
        user_vol = str(form_data.get("net_contents", "")).strip()
        if user_vol and extracted_vol:
            user_digits = re.sub(r'\D', '', user_vol)
            vol_matches_form = (user_digits == extracted_vol)

        # Check Brand (looks for partial/fuzzy string matches in extracted text)
        user_brand = str(form_data.get("brand", "")).strip().lower()
        if user_brand:
            # Matches if user brand is inside full text OR extracted brand snippet matches
            brand_matches_form = (user_brand in full_text_lower) or any(user_brand in line.lower() for line in extracted_text)

        # Check Product Class
        user_class = str(form_data.get("class", "")).strip().lower()
        if user_class:
            class_matches_form = user_class in full_text_lower

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