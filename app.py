import streamlit as st
from PIL import Image
from easy_ocr_engine import extract_text_from_image
from verification import verify_label_compliance

# Page configuration
st.set_page_config(
    page_title="LabelCheck AI",
    page_icon="🍷",
    layout="wide"
)

# Light mode UI styling
st.markdown("""
    <style>
    .stApp {
        background-color: #F5F6F8;
        color: #1E1E1E;
    }
    .stButton>button {
        background-color: #0066CC;
        color: white;
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🍷 LabelCheck AI")
st.caption("AI-Powered Alcohol Label Verification App")

st.markdown("---")

col1, col2 = st.columns([1, 1])

# Initialize image variable
image = None

with col1:
    st.subheader("Product Application Form")
    
    with st.form("label_verification_form"):
        # Brand Name
        st.markdown("Brand Name <span style='color:red;'>*</span>", unsafe_allow_html=True)
        brand_name = st.text_input("Brand Name", label_visibility="collapsed")
        st.caption("Minimum 4 characters")
        
        # Product Class/Type
        st.markdown("Product Class/Type <span style='color:red;'>*</span>", unsafe_allow_html=True)
        product_class = st.text_input("Product Class/Type", label_visibility="collapsed")
        st.caption("Minimum 3 characters")
        
        col_abv, col_net = st.columns(2)
        with col_abv:
            st.markdown("Alcohol Content (ABV %) <span style='color:red;'>*</span>", unsafe_allow_html=True)
            abv_input = st.number_input(
                "Alcohol Content (ABV %)", 
                min_value=0.0, 
                max_value=100.0, 
                step=0.1, 
                label_visibility="collapsed"
            )
            
        with col_net:
            st.markdown("Net Contents (Optional)", unsafe_allow_html=True)
            net_contents = st.text_input("Net Contents", label_visibility="collapsed")
            st.caption("E.g., 750 mL, 12 fl oz, 1 L")
            
        # File Uploader
        st.markdown("Select a label image to verify <span style='color:red;'>*</span>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Select a label image to verify", 
            type=["png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"],
            label_visibility="collapsed"
        )
        
        submit_btn = st.form_submit_button("Verify Label", type="primary", width="stretch")

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Label", width="stretch")

with col2:
    st.subheader("Verification Results")
    st.caption("Results will be displayed here after submission.")
    
    # Validation logic executed upon clicking submission
    if submit_btn:
        is_valid = True
        
        if len(brand_name.strip()) < 4:
            st.error("⚠️ Brand Name must be at least 4 characters long.")
            is_valid = False
            
        if len(product_class.strip()) < 3:
            st.error("⚠️ Product Class/Type must be at least 3 characters long.")
            is_valid = False
            
        if abv_input <= 0.0:
            st.error("⚠️ Alcohol Content (ABV %) must be greater than 0.0%.")
            is_valid = False
            
        if uploaded_file is None or image is None:
            st.error("⚠️ Please upload a label image to proceed.")
            is_valid = False

        # Execute OCR and verification engine only when all validations pass
        if is_valid:
            with st.spinner("Extracting text and verifying rules..."):
                extracted_lines = extract_text_from_image(image)
                
                form_data = {
                    "brand": brand_name.strip(),
                    "product_class": product_class.strip(),
                    "abv": abv_input,
                    "net_contents": net_contents.strip()
                }
                
                results = verify_label_compliance(extracted_lines, form_data=form_data)
            
            # Display Compliance Badge
            if results["is_compliant"]:
                st.success("✔️ COMPLIANT LABEL - ALL MATCHES PASSED")
            else:
                st.error("❌ NON-COMPLIANT LABEL - MISMATCH OR MISSING DATA")
            
            # Checklist Table
            st.markdown("**Rule & Form Verification Checklist:**")
            for check, passed in results["checks"].items():
                if passed:
                    st.write(f"✔️ **{check}**: Passed")
                else:
                    st.write(f"❌ **{check}**: Mismatch / Failed")
                    
            # Extracted Details Expander
            with st.expander("View Extracted OCR Metadata"):
                st.json(results["extracted_details"])
