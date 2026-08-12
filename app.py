import streamlit as st
from PIL import Image
from easy_ocr_engine import extract_text_from_image
from verification import verify_label_compliance

# Page configuration
st.set_page_config(
    page_title="LabelCheck AI",
    page_icon="🔍",
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

st.title("🔍 LabelCheck AI")
st.caption("AI-Powered Alcohol Label Verification System")

st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Product Application Form")
    
    with st.form("label_verification_form"):
        brand_name = st.text_input("Brand Name *", help="Minimum 4 characters")
        product_class = st.text_input("Product Class/Type *", help="E.g., Bourbon Whiskey, Vodka, IPA")
        
        col_abv, col_net = st.columns(2)
        with col_abv:
            abv_input = st.number_input("Alcohol Content (ABV %) *", min_value=0.0, max_value=100.0, step=0.1)
        with col_net:
            net_contents = st.text_input("Net Contents (Optional)", help="E.g., 750 mL, 12 fl oz, 1 L")
            
        uploaded_file = st.file_uploader(
            "Select a label image to verify *", 
            type=["png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"]
        )
        
        submit_btn = st.form_submit_button("Verify Label", type="primary", use_container_width=True)

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Label", use_container_width=True)

with col2:
    st.subheader("Verification Results")
    
    if submit_btn and uploaded_file is not None:
        with st.spinner("Extracting text and verifying rules..."):
            extracted_lines = extract_text_from_image(image)
            
            # Package form inputs into a dictionary
            form_data = {
                "brand": brand_name,
                "class": product_class,
                "abv": abv_input,
                "net_contents": net_contents
            }
            
            # Pass form_data to the verification engine
            results = verify_label_compliance(extracted_lines, form_data=form_data)
        
        # Display Compliance Badge
        if results["is_compliant"]:
            st.success("✅ COMPLIANT LABEL")
        else:
            st.error("❌ NON-COMPLIANT LABEL")
            
        # Display Submitted Details Summary
        st.markdown("**Submitted Application Details:**")
        st.write(f"- **Brand:** {brand_name if brand_name else 'N/A'}")
        st.write(f"- **Class/Type:** {product_class if product_class else 'N/A'}")
        st.write(f"- **ABV:** {abv_input}%")
        st.write(f"- **Net Contents:** {net_contents if net_contents else 'N/A'}")
        
        # Checklist Table
        st.markdown("**Rule Verification Checklist:**")
        for check, passed in results["checks"].items():
            if passed:
                st.write(f"✔️ **{check}**: Passed")
            else:
                st.write(f"❌ **{check}**: Missing/Failed")
                
        # Extracted Information Details
        with st.expander("View Extracted Metadata & OCR Raw Text"):
            st.json(results["extracted_details"])