import re
from thefuzz import fuzz

def extract_abv(full_text: str) -> float | None:
    """
    Generalized ABV extraction using flexible patterns and Proof fallback arithmetic.
    """
    abv_match = re.search(r'(\d{1,2}[\.,]?\d?)\s*(?:%|\*|\bpercent\b|\balc\b|\bvol\b)', full_text, re.IGNORECASE)
    if abv_match:
        val_str = abv_match.group(1).replace(',', '.')
        try:
            val = float(val_str)
            if 0.5 <= val <= 95.0:
                return val
        except ValueError:
            pass

    proof_match = re.search(r'(\d{2,3})\s*(?:proof|prf|pruun|prun)', full_text, re.IGNORECASE)
    if proof_match:
        try:
            proof_val = float(proof_match.group(1))
            if 10.0 <= proof_val <= 200.0:
                return proof_val / 2.0
        except ValueError:
            pass

    return None

def extract_volume(full_text: str) -> str | None:
    """
    Generalized Net Volume extraction using standard liquid bottle numbers and unit regex.
    """
    standard_match = re.search(r'\b(1000|750|700|500|375|355|50)\b', full_text)
    if standard_match:
        return standard_match.group(1)

    vol_match = re.search(r'(\d{2,4})\s*(?:ml|l|fl\s*oz|oz|cl)\b', full_text, re.IGNORECASE)
    if vol_match:
        return vol_match.group(1)

    return None

def extract_government_warning(extracted_text: list[str]) -> str:
    """
    Extracts and joins all lines belonging to the Government Warning text block.
    Returns 'Not Present' if no warning header is detected.
    """
    warning_lines = []
    recording = False

    for line in extracted_text:
        if (re.search(r'(gov\w*|surgeon)\s*(war\w*|general)', line, re.IGNORECASE) or
            fuzz.partial_ratio("government warning", line.lower()) >= 45 or
            fuzz.partial_ratio("surgeon general", line.lower()) >= 45):
            recording = True

        if recording:
            warning_lines.append(line.strip())

    return " ".join(warning_lines) if warning_lines else "Not Present"

def extract_product_class_from_image(full_text: str) -> str | None:
    """Extracts known spirit/beverage class types directly from OCR text."""
    classes = [
        "vodka", "whiskey", "whisky", "bourbon", "rum", "gin", 
        "tequila", "brandy", "cognac", "liqueur", "mezcal", "scotch", "wine", "beer"
    ]
    for p_class in classes:
        if re.search(r'\b' + p_class + r'\b', full_text, re.IGNORECASE):
            return p_class.capitalize()
    return None

def extract_brand_from_image(extracted_text: list[str]) -> str | None:
    """Extracts candidate brand text line directly from OCR lines."""
    for line in extracted_text:
        line_clean = line.strip()
        # Skip warning lines, numerical specs, or common metadata
        if (len(line_clean) >= 3 and 
            not re.search(r'(warning|surgeon|alc|vol|proof|net|contents|\d)', line_clean, re.IGNORECASE)):
            return line_clean
    return extracted_text[0].strip() if extracted_text else None

def verify_label_compliance(extracted_text: list[str], form_data: dict = None) -> dict:
    full_text_lower = " ".join(extracted_text).lower()
    lower_extracted_lines = [line.lower() for line in extracted_text]

    # Government Warning Extraction
    extracted_warning = extract_government_warning(extracted_text)
    has_warning = (extracted_warning != "Not Present")

    extracted_abv = extract_abv(full_text_lower)
    extracted_vol = extract_volume(full_text_lower)

    abv_matches = False
    vol_matches = False
    brand_matches = False
    class_matches = False

    if form_data:
        # ABV Check (Exact match check safely handles strings and floats)
        user_abv_raw = form_data.get("abv")
        if user_abv_raw is not None and extracted_abv is not None:
            try:
                abv_matches = (float(user_abv_raw) == extracted_abv)
            except (ValueError, TypeError):
                abv_matches = False

        # Volume Check
        user_vol_raw = str(form_data.get("net_contents", "")).strip()
        user_vol_digits = re.sub(r'\D', '', user_vol_raw)
        
        if user_vol_digits and extracted_vol:
            vol_matches = (user_vol_digits == extracted_vol)
        elif not user_vol_digits:
            vol_matches = False

        # Generalized Fuzzy Brand Match
        user_brand = str(form_data.get("brand", "")).strip().lower()
        if user_brand:
            brand_matches = (
                user_brand in full_text_lower or 
                any(fuzz.partial_ratio(user_brand, line) >= 50 for line in lower_extracted_lines)
            )

        # Generalized Fuzzy Product Class Match
        user_class = str(form_data.get("product_class", "") or form_data.get("class", "")).strip().lower()
        if user_class:
            class_matches = (
                user_class in full_text_lower or 
                any(fuzz.partial_ratio(user_class, line) >= 50 for line in lower_extracted_lines)
            )

    is_compliant = all([has_warning, abv_matches, vol_matches, brand_matches, class_matches])

    # Extract OCR lines for displaying actual image metadata
    extracted_brand_text = extract_brand_from_image(extracted_text)
    extracted_class_text = extract_product_class_from_image(full_text_lower)

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
            "Extracted Brand Name": extracted_brand_text if extracted_brand_text else "Not Found",
            "Extracted Product/Class Type": extracted_class_text if extracted_class_text else "Not Found",
            "Extracted ABV": f"{extracted_abv}%" if extracted_abv is not None else "Not Found",
            "Extracted Net Contents": f"{extracted_vol} mL" if extracted_vol is not None else "Not Found",
            "Extracted Government Warning": extracted_warning
        }
    }