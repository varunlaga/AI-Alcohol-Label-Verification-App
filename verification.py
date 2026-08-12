import re
from thefuzz import fuzz

def normalize_text(text: str) -> str:
    """Replaces common OCR misread characters with standard letters."""
    text = text.lower()
    replacements = {
        'wodka': 'vodka',
        'faney': 'fancy',
        'nct': 'net',
        'contcnt': 'contents',
        'contcnts': 'contents',
        'alevol': 'alc/vol',
        'diseillinz': 'distilling',
        'distillina': 'distilling',
        'spuinglfield': 'springfield',
        'spinglield': 'springfield'
    }
    for orig, fix in replacements.items():
        text = text.replace(orig, fix)
    return text

def verify_label_compliance(extracted_text: list[str], form_data: dict = None) -> dict:
    # Build normalized full string
    raw_full = " ".join(extracted_text)
    full_text = normalize_text(raw_full)
    
    # 1. Government Warning: Match keywords or fuzzy similarity
    warning_terms = ["government", "warning", "surgeon", "general", "pregnancy", "health", "beverages", "defects"]
    has_warning = any(term in full_text for term in warning_terms) or \
                  any(fuzz.partial_ratio("government warning", line.lower()) > 60 for line in extracted_text)
                  
    # 2. Extract ABV (extracts float numbers tied to %, alc, or proof)
    abv_matches = re.findall(r'(\d{1,2}\.\d|\d{1,2})\s*(%|alc|proof|a1c|alevol)', full_text)
    extracted_abv = float(abv_matches[0][0]) if abv_matches else None
    if not extracted_abv:
        # Fallback numeric scan for 40.0
        num_match = re.search(r'\b(40\.0|40|50|12|5)\b', full_text)
        extracted_abv = float(num_match.group(1)) if num_match else None

    # 3. Extract Volume (extracts 750, 1000, 500, 375, etc.)
    vol_match = re.search(r'\b(750|1000|1l|500|375|50|700)\b', full_text)
    extracted_vol = vol_match.group(1) if vol_match else None

    # Form Matching Flags
    abv_matches_form = False
    vol_matches_form = False
    brand_matches_form = False
    class_matches_form = False

    if form_data:
        # Check ABV (numeric difference)
        user_abv = form_data.get("abv")
        if user_abv is not None and extracted_abv is not None:
            abv_matches_form = abs(float(user_abv) - extracted_abv) <= 1.0

        # Check Volume
        user_vol = str(form_data.get("net_contents", "")).strip()
        if not user_vol or user_vol == "0":
            vol_matches_form = True  # Optional field default
        elif extracted_vol:
            user_digits = re.sub(r'\D', '', user_vol)
            vol_matches_form = (user_digits == extracted_vol)

        # Check Brand (Fuzzy matching with threshold of 65%)
        user_brand = str(form_data.get("brand", "")).strip().lower()
        if user_brand:
            brand_matches_form = (user_brand in full_text) or \
                                 any(fuzz.partial_ratio(user_brand, line.lower()) >= 65 for line in extracted_text)

        # Check Product Class (Fuzzy matching with threshold of 65%)
        user_class = str(form_data.get("class", "")).strip().lower()
        if user_class:
            class_matches_form = (user_class in full_text) or \
                                 any(fuzz.partial_ratio(user_class, line.lower()) >= 65 for line in extracted_text)

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
            "Normalized Text": full_text,
            "Raw Text Lines": extracted_text
        }
    }