import re
from thefuzz import fuzz

def extract_abv(full_text: str) -> float | None:
    """
    Generalized ABV extraction using flexible patterns and Proof fallback arithmetic.
    """
    # Direct ABV Percentage pattern (e.g., '40.0%', '40% ALC', '5.5% abv', '40,0')
    abv_match = re.search(r'(\d{1,2}[\.,]?\d?)\s*(?:%|\*|\bpercent\b|\balc\b|\bvol\b)', full_text, re.IGNORECASE)
    if abv_match:
        val_str = abv_match.group(1).replace(',', '.')
        try:
            val = float(val_str)
            if 0.5 <= val <= 95.0:
                return val
        except ValueError:
            pass

    # Proof Fallback (Proof / 2 = ABV) e.g., '80 Proof', '100 PROOF', '80 prf'
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
    # Match standard bottle volumes directly (750, 1000, 500, 375, 700, 355, 50)
    standard_match = re.search(r'\b(1000|750|700|500|375|355|50)\b', full_text)
    if standard_match:
        return standard_match.group(1)

    # General unit match (digits near ml, l, fl oz, cl)
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
        # Detect start of government warning block via regex or fuzzy match
        if (re.search(r'(gov\w*|surgeon)\s*(war\w*|general)', line, re.IGNORECASE) or
            fuzz.partial_ratio("government warning", line.lower()) >= 45 or
            fuzz.partial_ratio("surgeon general", line.lower()) >= 45):
            recording = True

        if recording:
            warning_lines.append(line.strip())

    if warning_lines:
        return " ".join(warning_lines)
    
    return "Not Present"

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
        # ABV Check (Tolerates +/- 0.5% deviation)
        user_abv = form_data.get("abv")
        if user_abv is not None and user_abv > 0 and extracted_abv is not None:
            abv_matches = abs(float(user_abv) - extracted_abv) <= 0.5

        # Volume Check (Compares raw digits only; passes if omitted in form)
        user_vol_raw = str(form_data.get("net_contents", "")).strip()
        user_vol_digits = re.sub(r'\D', '', user_vol_raw)
        
        if user_vol_digits and extracted_vol:
            vol_matches = (user_vol_digits == extracted_vol)
        elif not user_vol_digits:
            vol_matches = True

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

    # Values for extracted metadata summary
    user_brand_val = form_data.get("brand", "").strip() if form_data else ""
    user_class_val = (form_data.get("product_class", "") or form_data.get("class", "")).strip() if form_data else ""

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
            "Extracted Brand Name": user_brand_val if brand_matches else "Not Found",
            "Extracted Product/Class Type": user_class_val if class_matches else "Not Found",
            "Extracted ABV": f"{extracted_abv}%" if extracted_abv is not None else "Not Found",
            "Extracted Net Contents": f"{extracted_vol} mL" if extracted_vol is not None else "Not Found",
            "Extracted Government Warning": extracted_warning
        }
    }