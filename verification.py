import re

def verify_label_compliance(extracted_text: list[str], form_data: dict = None) -> dict:
    """
    Universal verification logic for any label type (Vodka, Bourbon, Wine, etc.)
    No hardcoded word replacements.
    """
    full_text = " ".join(extracted_text)
    full_text_lower = full_text.lower()
    
    # 1. Government Warning: Matches variations of "Government Warning" or "Surgeon General"
    # Handles OCR noise like punctuation, spaces, or minor misreads
    warning_pattern = re.compile(r'(gov\w*|surgeon)\s*(war\w*|general)', re.IGNORECASE)
    has_warning = bool(warning_pattern.search(full_text_lower))
    
    # 2. Universal ABV Extraction (e.g., 40.0%, 45% alc/vol, 80 proof -> 40%)
    extracted_abv = None
    abv_match = re.search(r'(\d{1,2}(\.\d)?)\s*(%|\bpercent\b|\balc\b)', full_text_lower)
    if abv_match:
        extracted_abv = float(abv_match.group(1))
        
    # 3. Universal Volume Extraction (e.g., 750 mL, 750ml, 1 Liter, 12 fl oz, 75cl)
    extracted_vol = None
    vol_match = re.search(r'(\d+)\s*(ml|l|liter|liters|fl\s*oz|cl)\b', full_text_lower)
    if vol_match:
        extracted_vol = vol_match.group(1)
    else:
        # Fallback: Find standalone 3-digit volumes like 750 or 375 if 'ml' was omitted by OCR
        fallback_vol = re.findall(r'\b(750|1000|500|375|700)\b', full_text)
        if fallback_vol:
            extracted_vol = fallback_vol[0]

    # Initialize Verification Flags
    abv_matches_form = False
    vol_matches_form = False
    brand_matches_form = False
    class_matches_form = False

    if form_data:
        # Check ABV
        user_abv = form_data.get("abv")
        if user_abv is not None and user_abv > 0 and extracted_abv is not None:
            abv_matches_form = abs(float(user_abv) - extracted_abv) <= 0.5
        elif user_abv == 0 and extracted_abv is not None:
            abv_matches_form = False  # Left empty/zero on form

        # Check Volume (Strict Logic: If OCR missed volume, match fails)
        user_vol = str(form_data.get("net_contents", "")).strip()
        user_digits = re.sub(r'\D', '', user_vol)
        
        if not user_digits:
            # If user left Net Contents empty in form, require volume present on label
            vol_matches_form = extracted_vol is not None
        else:
            # Compare digits directly (e.g., "750" == "750")
            vol_matches_form = (extracted_vol == user_digits)

        # Check Brand (Case-insensitive substring search across full OCR text)
        user_brand = str(form_data.get("brand", "")).strip().lower()
        if user_brand:
            brand_matches_form = user_brand in full_text_lower

        # Check Product Class (e.g., "Bourbon Whiskey", "Vodka")
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