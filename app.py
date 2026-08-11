import streamlit as st
from PIL import Image
from ocr_engine import extract_text_from_image
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
        background-color: #FFFFFF;
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
st.caption("AI-Powered Compliance Label Verification System")

st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Upload Label")
    uploaded_file = st.file_uploader("Select a label image to verify", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Label", width="stretch")

with col2:
    st.subheader("Verification Results")
    
    if uploaded_file is not None:
        with st.spinner("Extracting text and verifying rules..."):
            extracted_lines = extract_text_from_image(image)
            results = verify_label_compliance(extracted_lines)
        
        # Display Compliance Badge
        if results["is_compliant"]:
            st.success("✅ COMPLIANT LABEL")
        else:
            st.error("❌ NON-COMPLIANT LABEL")
        
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
    else:
        st.info("Upload an image on the left to trigger the automated check.")