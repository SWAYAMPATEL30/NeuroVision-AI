"""
Medical Disease Classification System - Web UI
Simple interface to test the classification system
"""

import streamlit as st
import sys
import os
from PIL import Image
import json
import io

# Fix encoding issues on Windows before importing classifier
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def display_results(results, show_details):
    """Display classification results"""
    st.markdown("---")
    st.subheader("📊 Classification Results")
    
    classifications = results.get("classifications", {})
    
    # Quick summary
    cols = st.columns(3)
    
    # MedSigLIP
    with cols[0]:
        if "medsiglip" in classifications and "error" not in classifications["medsiglip"]:
            if "top_prediction" in classifications["medsiglip"]:
                st.metric("MedSigLIP", classifications["medsiglip"]["top_prediction"])
    
    # CXR
    with cols[1]:
        if "cxr" in classifications and "error" not in classifications["cxr"]:
            if "top_predictions" in classifications["cxr"]:
                top = list(classifications["cxr"]["top_predictions"].keys())[0] if classifications["cxr"]["top_predictions"] else "N/A"
                st.metric("CXR Foundation", top)
    
    # CheXpert
    with cols[2]:
        if "chexpert" in classifications and "error" not in classifications["chexpert"]:
            if "top_predictions" in classifications["chexpert"]:
                top = list(classifications["chexpert"]["top_predictions"].keys())[0] if classifications["chexpert"]["top_predictions"] else "N/A"
                st.metric("CheXpert", top)
    
    # Detailed predictions
    if show_details:
        st.markdown("### Detailed Predictions")
        
        # MedSigLIP comprehensive
        if "medsiglip" in classifications and "predictions" in classifications["medsiglip"]:
            st.markdown("**MedSigLIP Comprehensive Detection:**")
            medsiglip_preds = classifications["medsiglip"]["predictions"]
            # Show top 10
            sorted_preds = sorted(medsiglip_preds.items(), key=lambda x: x[1], reverse=True)[:10]
            for disease, score in sorted_preds:
                st.progress(score, text=f"{disease}: {score:.1%}")
            if "total_diseases_checked" in classifications["medsiglip"]:
                st.caption(f"Checked {classifications['medsiglip']['total_diseases_checked']} diseases")
        
        # CheXpert detailed
        if "chexpert" in classifications and "top_predictions" in classifications["chexpert"]:
            st.markdown("**CheXpert DenseNet Predictions:**")
            for disease, score in classifications["chexpert"]["top_predictions"].items():
                st.progress(score, text=f"{disease}: {score:.1%}")
    
    # Extracted diseases from text
    if "extracted_diseases" in results and results["extracted_diseases"].get("diseases"):
        st.markdown("---")
        st.subheader("🔍 Diseases Extracted from Text")
        diseases = results["extracted_diseases"]["diseases"]
        if diseases:
            st.write(f"**Found {len(diseases)} disease(s):**")
            for item in diseases[:10]:  # Show top 10
                category = item.get("category", "other")
                st.write(f"- **{item['disease']}** ({category})")
            if len(diseases) > 10:
                st.caption(f"... and {len(diseases) - 10} more")
    
    # Report preview
    if results.get("report"):
        st.markdown("---")
        with st.expander("📄 View Generated Report", expanded=False):
            st.markdown(results["report"])

# Set page config
st.set_page_config(
    page_title="Medical Disease Classifier",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .model-result {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .prediction-item {
        padding: 0.5rem;
        margin: 0.25rem 0;
        background-color: white;
        border-radius: 0.25rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">🏥 Medical Disease Classification System</div>', unsafe_allow_html=True)
st.markdown("---")

# Initialize session state
if 'classifier' not in st.session_state:
    st.session_state.classifier = None
if 'last_results' not in st.session_state:
    st.session_state.last_results = None

# Sidebar for model info
with st.sidebar:
    st.header("📊 System Information")
    st.markdown("""
    **Available Models:**
    - MedSigLIP (General Detection)
    - CXR Foundation (Chest Diseases)
    - CheXpert DenseNet (Common Diseases)
    
    **Note:** All classifications come from Hugging Face models.
    Groq API is used only for report generation.
    """)
    
    st.markdown("---")
    st.header("⚙️ Settings")
    generate_report = st.checkbox("Generate Radiology Report", value=True)
    show_details = st.checkbox("Show Detailed Predictions", value=False)

# Main content area
tab1, tab2, tab3 = st.tabs(["📷 Image Classification", "📝 Text Report", "📊 View Results"])

# Tab 1: Image Classification
with tab1:
    st.header("Upload Medical Image")
    st.markdown("Upload a medical image (X-ray, CT scan, etc.) for disease classification")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['png', 'jpg', 'jpeg', 'dcm'],
            help="Supported formats: PNG, JPG, JPEG, DICOM"
        )
        
        if uploaded_file is not None:
            try:
                # Display image
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_container_width=True)
                
                # Classification button
                if st.button("🔍 Classify Disease", type="primary", use_container_width=True):
                    with st.spinner("Loading classifier and analyzing image..."):
                        # Initialize classifier if not already done
                        if st.session_state.classifier is None:
                            try:
                                from medical_classifier import MedicalClassifier
                                st.session_state.classifier = MedicalClassifier()
                                st.success("✅ Models loaded successfully!")
                            except Exception as e:
                                st.error(f"❌ Failed to load classifier: {e}")
                                st.stop()
                        
                        # Run classification
                        try:
                            results = st.session_state.classifier.classify(
                                image_path=image,
                                generate_report=generate_report
                            )
                            st.session_state.last_results = results
                            st.success("✅ Classification complete!")
                            
                            # Display results
                            display_results(results, show_details)
                            
                        except Exception as e:
                            st.error(f"❌ Classification failed: {e}")
                            import traceback
                            st.code(traceback.format_exc())
            
            except Exception as e:
                st.error(f"❌ Error loading image: {e}")
    
    with col2:
        st.markdown("### 💡 Tips")
        st.markdown("""
        - **Best results**: Use clear, high-quality medical images
        - **Supported**: Chest X-rays, CT scans, bone X-rays
        - **Processing time**: 10-30 seconds depending on image size
        - **Models**: All predictions from Hugging Face models
        """)

# Tab 2: Text Report Classification
with tab2:
    st.header("Enter Medical Report Text")
    st.markdown("Paste or type a medical report to classify diseases")
    
    # Text input
    report_text = st.text_area(
        "Medical Report",
        height=200,
        placeholder="""Example:
Patient presents with acute chest pain and shortness of breath.
Chest X-ray shows bilateral lower lobe opacities consistent with pneumonia.
No pneumothorax or pleural effusion noted.
Cardiomegaly is present."""
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("🔍 Analyze Report", type="primary", use_container_width=True):
            if not report_text.strip():
                st.warning("⚠️ Please enter a medical report")
            else:
                with st.spinner("Analyzing report..."):
                    # Initialize classifier if not already done
                    if st.session_state.classifier is None:
                        try:
                            from medical_classifier import MedicalClassifier
                            st.session_state.classifier = MedicalClassifier()
                            st.success("✅ Models loaded successfully!")
                        except Exception as e:
                            st.error(f"❌ Failed to load classifier: {e}")
                            st.stop()
                    
                    # Run classification
                    try:
                        results = st.session_state.classifier.classify(
                            report_text=report_text,
                            generate_report=generate_report
                        )
                        st.session_state.last_results = results
                        st.success("✅ Analysis complete!")
                        
                        # Display results
                        display_results(results, show_details)
                        
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {e}")
                        import traceback
                        st.code(traceback.format_exc())
    
    with col2:
        st.markdown("### 📋 Sample Reports")
        sample1 = """Patient presents with acute chest pain and shortness of breath.
Chest X-ray shows bilateral lower lobe opacities consistent with pneumonia.
No pneumothorax or pleural effusion noted.
Cardiomegaly is present."""
        
        sample2 = """Patient with history of smoking, presenting with cough and fever.
Radiographic findings show right upper lobe consolidation.
Possible tuberculosis or bacterial pneumonia.
No evidence of pneumothorax."""
        
        if st.button("📄 Load Sample 1"):
            st.session_state.sample_text = sample1
            st.rerun()
        
        if st.button("📄 Load Sample 2"):
            st.session_state.sample_text = sample2
            st.rerun()
        
        if 'sample_text' in st.session_state:
            report_text = st.session_state.sample_text
            st.info("Sample report loaded! Click 'Analyze Report' to process it.")

# Tab 3: View Results
with tab3:
    st.header("Last Classification Results")
    
    if st.session_state.last_results is None:
        st.info("👆 No results yet. Please run a classification in the Image or Text tabs.")
    else:
        results = st.session_state.last_results
        
        # Summary
        st.subheader("📊 Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Input Type", results.get("input_type", "N/A").title())
        with col2:
            num_models = len([k for k in results.get("classifications", {}).keys() if "error" not in results.get("classifications", {}).get(k, {})])
            st.metric("Models Used", f"{num_models}/3")
        with col3:
            has_report = "report" in results and results["report"]
            st.metric("Report Generated", "✅ Yes" if has_report else "❌ No")
        
        st.markdown("---")
        
        # Detailed results
        st.subheader("🔍 Model Predictions")
        
        classifications = results.get("classifications", {})
        
        # MedGemma results (Primary - Highest Accuracy)
        if "medgemma" in classifications:
            medgemma = classifications["medgemma"]
            if "error" not in medgemma:
                with st.expander("🏆 MedGemma-27b-it - Primary Medical Model (Highest Accuracy)", expanded=True):
                    st.success("**Model Status:** Active - Medical-grade AI model")
                    if "primary_diagnosis" in medgemma:
                        st.info(f"**Primary Diagnosis:** {medgemma['primary_diagnosis']}")
                    if "full_analysis" in medgemma:
                        st.markdown("**Full Analysis:**")
                        st.text_area("", medgemma["full_analysis"], height=200, disabled=True, key="medgemma_analysis")
                    if "confidence" in medgemma:
                        st.metric("Confidence Level", medgemma["confidence"].title())
            else:
                st.warning(f"MedGemma: {medgemma.get('error', 'Unknown error')}")
                st.info("Note: MedGemma requires accepting terms at https://huggingface.co/google/medgemma-27b-it")
        
        # MedSigLIP results
        if "medsiglip" in classifications:
            medsiglip = classifications["medsiglip"]
            if "error" not in medsiglip:
                with st.expander("🔬 MedSigLIP - General Detection", expanded=False):
                    if "top_prediction" in medsiglip:
                        st.success(f"**Top Prediction:** {medsiglip['top_prediction']}")
                    if "predictions" in medsiglip and show_details:
                        st.markdown("**All Predictions:**")
                        for disease, score in medsiglip["predictions"].items():
                            st.progress(score, text=f"{disease}: {score:.1%}")
            else:
                st.warning(f"MedSigLIP: {medsiglip.get('error', 'Unknown error')}")
        
        # CXR Foundation results
        if "cxr" in classifications:
            cxr = classifications["cxr"]
            if "error" not in cxr:
                with st.expander("🫁 CXR Foundation - Chest Diseases", expanded=True):
                    if "top_predictions" in cxr:
                        st.markdown("**Top Predictions:**")
                        for disease, score in cxr["top_predictions"].items():
                            st.progress(score, text=f"{disease}: {score:.1%}")
                    elif "note" in cxr:
                        st.info(cxr["note"])
            else:
                st.warning(f"CXR Foundation: {cxr.get('error', 'Unknown error')}")
        
        # CheXpert results
        if "chexpert" in classifications:
            chexpert = classifications["chexpert"]
            if "error" not in chexpert:
                with st.expander("🏥 CheXpert DenseNet - Common Diseases", expanded=True):
                    if "top_predictions" in chexpert:
                        st.markdown("**Top 5 Predictions:**")
                        for disease, score in chexpert["top_predictions"].items():
                            st.progress(score, text=f"{disease}: {score:.1%}")
                    
                    if show_details and "predictions" in chexpert:
                        st.markdown("**All 14 Disease Predictions:**")
                        for disease, score in sorted(chexpert["predictions"].items(), key=lambda x: x[1], reverse=True):
                            st.progress(score, text=f"{disease}: {score:.1%}")
            else:
                st.warning(f"CheXpert: {chexpert.get('error', 'Unknown error')}")
        
        # Generated report
        if results.get("report"):
            st.markdown("---")
            st.subheader("📄 Generated Radiology Report")
            st.markdown(results["report"])
            
            # Download buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.download_button(
                    label="📥 Download Text Report",
                    data=results["report"],
                    file_name="radiology_report.txt",
                    mime="text/plain"
                )
            
            with col2:
                # Generate PDF
                try:
                    from report_generator import generate_pdf_report
                    import tempfile
                    import os
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        pdf_path = tmp_file.name
                    
                    # Add report_text to results for PDF
                    results_with_text = results.copy()
                    if "report_text" not in results_with_text:
                        results_with_text["report_text"] = ""
                    
                    generate_pdf_report(results_with_text, pdf_path)
                    
                    with open(pdf_path, "rb") as pdf_file:
                        pdf_data = pdf_file.read()
                    
                    st.download_button(
                        label="📄 Download PDF Report",
                        data=pdf_data,
                        file_name="radiology_report.pdf",
                        mime="application/pdf"
                    )
                    
                    # Clean up
                    os.unlink(pdf_path)
                except Exception as e:
                    st.error(f"PDF generation failed: {e}")
                    st.info("Install reportlab: pip install reportlab")
            
            with col3:
                json_str = json.dumps(results, indent=2)
                st.download_button(
                    label="📊 Download JSON",
                    data=json_str,
                    file_name="classification_results.json",
                    mime="application/json"
                )
        
        # Best Prediction Summary
        if "best_prediction" in results:
            st.markdown("---")
            st.subheader("🎯 Best Model Prediction")
            best = results["best_prediction"]
            if best.get("disease"):
                st.success(f"**Primary Finding:** {best['disease']} ({best['confidence']:.1%} confidence)")
                st.info(f"**Source Model:** {best['model']}")
        
        # Download JSON results (if not already shown)
        if not results.get("report"):
            st.markdown("---")
            st.subheader("💾 Export Results")
            json_str = json.dumps(results, indent=2)
            st.download_button(
                label="📥 Download JSON Results",
                data=json_str,
                file_name="classification_results.json",
                mime="application/json"
            )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>Medical Disease Classification System | All classifications from Hugging Face models</p>
</div>
""", unsafe_allow_html=True)

