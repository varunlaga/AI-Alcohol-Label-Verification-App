import re
from thefuzz import fuzz

def extract_abv(full_text: str) -> float | None:
    """Extracts ABV percentage using case-insensitive regex patterns."""
    # Matches patterns like '40.0%', '40.0 *ALC', '40% alc/vol', '80 PROOF', '80 Proof'
    pct_match = re.search(r'(\d{1,2}(?:\.\d)?)\s*(?:%|\*|\bpercent\b|\balc\b)', full_text, re.IGNORECASE)
    if pct_match:
        return float(pct_match.group(1))
    
    # Fallback to proof pattern (Proof / 2 = ABV)
    proof_match = re.search(r'(\d{2,3})\s*proof', full_text, re.IGNORECASE)
    if proof_match:
        return float(proof_match.group(1)) / 2.0
        
    return None

def extract_volume(full_text: str) -> str | None:
    """Extracts volume digits regardless of unit case (ML, ml, mL, Fl Oz, L, etc.)."""
    # Look for common standard bottle size digits (750, 1000, 500, 375, 700, 50)
    standard_match = re.search(r'\b(750|1000|500|375|700|50)\b', full_text)
    if standard_match:
        return standard_match.group(1)
        
    # Standard unit search (case-insensitive flag handles ml, ML, mL, fl oz, FL OZ, etc.)
    vol_match = re.search(r'(\d+)\s*(?:ml|l|fl\s*oz|cl)\b', full_text, re.IGNORECASE)
    if vol_match:
        val = vol_match.group(1)
        # Fix OCR dropping trailing 0s (e.g. '75' -> '750')
        if val == "75":
            return "750"
        return val
        
    return None

def verify_label_compliance(extracted_text: list[str], form_data: dict = None) -> dict:
    # 1. Normalize all extracted text to lowercase for internal processing
    full_text_lower = " ".join(extracted_text).lower()
    lower_extracted_lines = [line.lower() for line in extracted_text]
    
    # 2. Case-Insensitive Government Warning Detection
    has_warning = (
        bool(re.search(r'(gov\w*|surgeon)\s*(war\w*|general)', full_text_lower, re.IGNORECASE)) or
        any(fuzz.partial_ratio("government warning", line) >= 55 for line in lower_extracted_lines) or
        any(fuzz.partial_ratio("surgeon general", line) >= 55 for line in lower_extracted_lines)
    )
    
    # 3. Extract Values
    extracted_abv = extract_abv(full_text_lower)
    extracted_vol = extract_volume(full_text_lower)

    # 4. Form Validation Flags
    abv_matches = False
    vol_matches = False
    brand_matches = False
    class_matches = False

    if form_data:
        # ABV Check
        user_abv = form_data.get("abv")
        if user_abv is not None and user_abv > 0 and extracted_abv is not None:
            abv_matches = abs(float(user_abv) - extracted_abv) <= 0.5

        # Volume Check (Extracts only numeric digits from form input to bypass unit case like '750 mL' vs '750ml')
        user_vol_raw = str(form_data.get("net_contents", "")).strip()
        user_vol_digits = re.sub(r'\D', '', user_vol_raw)
        
        if user_vol_digits and extracted_vol:
            vol_matches = (user_vol_digits == extracted_vol)
        elif not user_vol_digits and extracted_vol:
            vol_matches = True  # Optional form field left blank

        # Case-Insensitive Fuzzy Brand Match (e.g., 'FANCY', 'Fancy', 'fancy')
        user_brand = str(form_data.get("brand", "")).strip().lower()
        if user_brand:
            brand_matches = (
                user_brand in full_text_lower or 
                any(fuzz.partial_ratio(user_brand, line) >= 60 for line in lower_extracted_lines)
            )

        # Case-Insensitive Fuzzy Product Class Match (e.g., 'VODKA', 'Vodka', 'vodka')
        user_class = str(form_data.get("class", "")).strip().lower()
        if user_class:
            class_matches = (
                user_class in full_text_lower or 
                any(fuzz.partial_ratio(user_class, line) >= 60 for line in lower_extracted_lines)
            )

    is_compliant = all([has_warning, abv_matches, vol_matches, brand_matches, class_matches])

    return {
        "is_compliant": is_compliant,
        "checks": {
            "Government Warning Present": has_warning,
            "Brand Matches Form": brand_matches,
            "Product Class Matches Form": class_matches,
            "ABV Matches Form": abv_matches,
            "Net Volume Matches Form": vol_matches
        },
        "extracted_details": {
            "Extracted ABV": f"{extracted_abv}%" if extracted_abv is not None else "Not Found",
            "Extracted Volume": f"{extracted_vol} mL" if extracted_vol is not None else "Not Found",
            "Raw Text Lines": extracted_text
        }
    }