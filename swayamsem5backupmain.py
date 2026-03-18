"""
Specialized Medical Classification UI
Divided by medical imaging types with best models for each category
"""

import streamlit as st
import sys
import os
from PIL import Image
import json
import io
import traceback

# Fix encoding issues on Windows
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def display_results(results, show_details):
    """Display classification results"""
    st.markdown("---")
    st.subheader("Classification Results")
    
    classifications = results.get("classifications", {})
    
    # Quick summary
    cols = st.columns(3)
    
    # Show best model result
    if "best_prediction" in results:
        best = results["best_prediction"]
        with cols[0]:
            st.metric("Best Model", best.get("model", "N/A"))
        with cols[1]:
            st.metric("Primary Finding", best.get("disease", "N/A"))
        with cols[2]:
            st.metric("Confidence", f"{best.get('confidence', 0):.1%}")
    
    # Detailed predictions
    if show_details:
        st.markdown("### Detailed Predictions")
        
        # MedGemma results
        if "medgemma" in classifications and "error" not in classifications["medgemma"]:
            medgemma = classifications["medgemma"]
            st.markdown("**MedGemma-27b-it Analysis:**")
            if "full_analysis" in medgemma:
                st.text_area("", medgemma["full_analysis"], height=150, disabled=True)
    
    # Report preview and downloads
    if results.get("report"):
        st.markdown("---")
        st.subheader("Generated Report")
        st.markdown(results["report"])
        
        # Download buttons
        col1, col2 = st.columns(2)
        
        with col1:
            # Download text report
            st.download_button(
                label="📥 Download Text Report",
                data=results["report"],
                file_name="medical_report.txt",
                mime="text/plain",
                width='stretch'
            )
        
        with col2:
            # Download PDF report
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
                    file_name="medical_report.pdf",
                    mime="application/pdf",
                    width='stretch'
                )
                
                # Clean up
                try:
                    os.unlink(pdf_path)
                except:
                    pass
            except Exception as e:
                st.error(f"PDF generation failed: {e}")
                st.info("Install reportlab: pip install reportlab")

# Set page config
st.set_page_config(
    page_title="Specialized Medical Classifier",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2c3e50;
        padding: 0.5rem 0;
        border-bottom: 2px solid #1f77b4;
    }
    .model-badge {
        background-color: #e8f4f8;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.25rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">🏥 Specialized Medical Disease Classification System</div>', unsafe_allow_html=True)
st.markdown("---")

# Initialize session state with error handling
try:
    if 'classifier' not in st.session_state:
        st.session_state.classifier = None
    if 'last_results' not in st.session_state:
        st.session_state.last_results = None
    if 'error_count' not in st.session_state:
        st.session_state.error_count = 0
except Exception as e:
    st.session_state = {
        'classifier': None,
        'last_results': None,
        'error_count': 0
    }


# Sidebar - Model Information
with st.sidebar:
    st.header("📊 Model Information")
    st.markdown("""
    **Available Models:**
    - **MedSigLIP**: Primary model (best accuracy & speed)
    - **MedGemma-27b-it**: Secondary model (high accuracy)
    - **CheXpert DenseNet**: Chest diseases specialist
    - **CXR Foundation**: Chest X-ray specialized
    
    **Model Selection:**
    - Chest X-ray → MedSigLIP + CheXpert + CXR + MedGemma
    - Bone X-ray → MedSigLIP + MedGemma
    - Brain Tumor → Brain Tumor Model (InceptionV3) + MedSigLIP + MedGemma
    - Reports → Text extraction + MedGemma
    """)
    
    st.markdown("---")
    st.header("⚙️ Settings")
    generate_report = st.checkbox("Generate Professional Report", value=True)
    show_details = st.checkbox("Show Detailed Analysis", value=False)

# Main tabs - Specialized by imaging type
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🫁 Chest X-Ray", 
    "🦴 Bone X-Ray", 
    "🧠 Brain Tumor", 
    "📝 Medical Reports", 
    "🔬 General Analysis"
])

# ============================================
# TAB 1: CHEST X-RAY (Specialized)
# ============================================
with tab1:
    st.markdown('<div class="section-header">🫁 Chest X-Ray Analysis</div>', unsafe_allow_html=True)
    st.markdown("**Best Models:** MedSigLIP (Primary) + CheXpert DenseNet + CXR Foundation + MedGemma")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload Chest X-Ray Image",
            type=['png', 'jpg', 'jpeg', 'dcm'],
            help="Upload a chest X-ray image for specialized analysis",
            key="chest_xray"
        )
        
        if uploaded_file is not None:
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption="Chest X-Ray Image", use_container_width=True)
                
                if st.button("🔍 Analyze Chest X-Ray", type="primary", use_container_width=True, key="analyze_chest"):
                    with st.spinner("Loading models and analyzing chest X-ray..."):
                        # Initialize classifier
                        if st.session_state.classifier is None:
                            try:
                                import importlib
                                import medical_classifier
                                importlib.reload(medical_classifier)
                                from medical_classifier import MedicalClassifier
                                st.session_state.classifier = MedicalClassifier()
                                st.success("✅ Models loaded successfully!")
                            except Exception as e:
                                st.error(f"❌ Failed to load classifier: {e}")
                                st.code(traceback.format_exc())
                                st.warning("⚠️ App will continue but some features may not work. Please refresh the page.")
                        
                        # Run specialized chest analysis
                        try:
                            if not hasattr(st.session_state.classifier, 'classify_chest_xray'):
                                st.error("❌ classify_chest_xray method not found. Please restart the app.")
                                st.warning("⚠️ Please refresh the page to reload models.")
                            
                            results = st.session_state.classifier.classify_chest_xray(
                                image_path=image,
                                generate_report=generate_report
                            )
                            st.session_state.last_results = results
                            st.success("✅ Chest X-ray analysis complete!")
                            
                            # Show model used
                            if "model_used" in results:
                                st.info(f"**Models Used:** {results['model_used']}")
                            
                            display_results(results, show_details)
                            
                            # Download options
                            if results.get("report"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.download_button(
                                        label="📥 Download Text Report",
                                        data=results["report"],
                                        file_name="chest_xray_report.txt",
                                        mime="text/plain",
                                        width='stretch',
                                        key="dl_chest_txt"
                                    )
                                with col2:
                                    try:
                                        from report_generator import generate_pdf_report
                                        import tempfile
                                        import os
                                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                                            pdf_path = tmp.name
                                        results_pdf = results.copy()
                                        results_pdf["report_text"] = ""
                                        generate_pdf_report(results_pdf, pdf_path)
                                        with open(pdf_path, "rb") as f:
                                            pdf_data = f.read()
                                        st.download_button(
                                            label="📄 Download PDF Report",
                                            data=pdf_data,
                                            file_name="chest_xray_report.pdf",
                                            mime="application/pdf",
                                            width='stretch',
                                            key="dl_chest_pdf"
                                        )
                                        os.unlink(pdf_path)
                                    except Exception as e:
                                        st.error(f"PDF failed: {e}")
                            
                        except Exception as e:
                            st.error(f"❌ Analysis failed: {e}")
                            import traceback
                            st.code(traceback.format_exc())
            
            except Exception as e:
                st.error(f"❌ Error loading image: {e}")
    
    with col2:
        st.markdown("### 💡 Chest X-Ray Tips")
        st.markdown("""
        - **Best for**: Pneumonia, pneumothorax, cardiomegaly
        - **Models used**: 
          - MedSigLIP (primary - best accuracy)
          - CheXpert (chest diseases)
          - CXR Foundation (specialized)
          - MedGemma (secondary)
        - **Accuracy**: Highest for chest conditions
        """)

# ============================================
# TAB 2: BONE X-RAY (Specialized)
# ============================================
with tab2:
    st.markdown('<div class="section-header">🦴 Bone X-Ray Analysis</div>', unsafe_allow_html=True)
    st.markdown("**Best Models:** MedSigLIP (Primary) + MedGemma-27b-it")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload Bone X-Ray Image",
            type=['png', 'jpg', 'jpeg', 'dcm'],
            help="Upload a bone X-ray image (fractures, joints, etc.)",
            key="bone_xray"
        )
        
        if uploaded_file is not None:
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption="Bone X-Ray Image", use_container_width=True)
                
                if st.button("🔍 Analyze Bone X-Ray", type="primary", use_container_width=True, key="analyze_bone"):
                    with st.spinner("Loading models and analyzing bone X-ray..."):
                        # Initialize classifier
                        if st.session_state.classifier is None:
                            try:
                                # Force reload to get latest methods
                                import importlib
                                import medical_classifier
                                importlib.reload(medical_classifier)
                                from medical_classifier import MedicalClassifier
                                st.session_state.classifier = MedicalClassifier()
                                st.success("✅ Models loaded successfully!")
                            except Exception as e:
                                st.error(f"❌ Failed to load classifier: {e}")
                                import traceback
                                st.code(traceback.format_exc())
                                st.warning("⚠️ Please refresh the page to reload models.")
                                # Don't stop - let user continue
                        
                        # Run specialized bone analysis
                        try:
                            # Use MedGemma (primary) + MedSigLIP for bones
                            if not hasattr(st.session_state.classifier, 'classify_bone_xray'):
                                st.error("❌ classify_bone_xray method not found. Trying to reload...")
                                try:
                                    import importlib
                                    import medical_classifier
                                    importlib.reload(medical_classifier)
                                    from medical_classifier import MedicalClassifier
                                    st.session_state.classifier = MedicalClassifier()
                                except Exception as reload_error:
                                    st.warning("⚠️ Please refresh the page to reload models.")
                                    st.error(f"Reload failed: {reload_error}")
                                    # Stop here if reload failed
                                    raise Exception("Cannot proceed without classifier method")
                            
                            # Call the classification method
                            results = st.session_state.classifier.classify_bone_xray(
                                image_path=image,
                                generate_report=generate_report
                            )
                            st.session_state.last_results = results
                            st.success("✅ Bone X-ray analysis complete!")
                            
                            # Show model used
                            if "model_used" in results:
                                st.info(f"**Models Used:** {results['model_used']}")
                            
                            display_results(results, show_details)
                            
                            # Download options
                            if results.get("report"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.download_button(
                                        label="📥 Download Text Report",
                                        data=results["report"],
                                        file_name="bone_xray_report.txt",
                                        mime="text/plain",
                                        width='stretch',
                                        key="dl_bone_txt"
                                    )
                                with col2:
                                    try:
                                        from report_generator import generate_pdf_report
                                        import tempfile
                                        import os
                                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                                            pdf_path = tmp.name
                                        results_pdf = results.copy()
                                        results_pdf["report_text"] = ""
                                        generate_pdf_report(results_pdf, pdf_path)
                                        with open(pdf_path, "rb") as f:
                                            pdf_data = f.read()
                                        st.download_button(
                                            label="📄 Download PDF Report",
                                            data=pdf_data,
                                            file_name="bone_xray_report.pdf",
                                            mime="application/pdf",
                                            width='stretch',
                                            key="dl_bone_pdf"
                                        )
                                        os.unlink(pdf_path)
                                    except Exception as e:
                                        st.error(f"PDF failed: {e}")
                            
                        except Exception as e:
                            st.error(f"❌ Analysis failed: {e}")
                            import traceback
                            st.code(traceback.format_exc())
            
            except Exception as e:
                st.error(f"❌ Error loading image: {e}")
    
    with col2:
        st.markdown("### 💡 Bone X-Ray Tips")
        st.markdown("""
        - **Best for**: Fractures, broken bones, joint issues
        - **Models used**: 
          - MedSigLIP (primary - best accuracy)
          - MedGemma (secondary)
        - **Detects**: Fractures, dislocations, bone diseases
        """)

# ============================================
# TAB 3: BRAIN TUMOR (MRI Analysis)
# ============================================
with tab3:
    st.markdown('<div class="section-header">🧠 Brain Tumor MRI Analysis</div>', unsafe_allow_html=True)
    st.markdown("**Primary Models (YOUR CUSTOM MODELS):** Brain Tumor Ensemble (InceptionV3 + ResNet50)")
    st.markdown("**Secondary Verification (LLMs):** MedSigLIP + MedGemma-27b-it (backup/verification only)")
    st.markdown("**Integrated from:** major_project-main (Your Custom Trained Models)")
    st.info("💡 **Note:** Your custom models are used as PRIMARY. LLMs provide secondary verification/backup.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload Brain MRI Image",
            type=['png', 'jpg', 'jpeg', 'dcm'],
            help="Upload a brain MRI image for tumor detection (glioma, meningioma, pituitary, or no tumor)",
            key="brain_tumor"
        )
        
        if uploaded_file is not None:
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption="Brain MRI Image", use_container_width=True)
                
                if st.button("🔍 Analyze Brain MRI", type="primary", use_container_width=True, key="analyze_brain"):
                    with st.spinner("Loading models and analyzing brain MRI..."):
                        # Initialize classifier
                        if st.session_state.classifier is None:
                            try:
                                # Force reload to get latest methods
                                import importlib
                                import medical_classifier
                                importlib.reload(medical_classifier)
                                from medical_classifier import MedicalClassifier
                                st.session_state.classifier = MedicalClassifier()
                                st.success("✅ Models loaded successfully!")
                            except Exception as e:
                                st.error(f"❌ Failed to load classifier: {e}")
                                import traceback
                                st.code(traceback.format_exc())
                                st.warning("⚠️ Please refresh the page to reload models.")
                                # Don't stop - let user continue
                        
                        # Run specialized brain tumor analysis
                        try:
                            if not hasattr(st.session_state.classifier, 'classify_brain_tumor'):
                                st.error("❌ classify_brain_tumor method not found. Trying to reload...")
                                try:
                                    import importlib
                                    import medical_classifier
                                    importlib.reload(medical_classifier)
                                    from medical_classifier import MedicalClassifier
                                    st.session_state.classifier = MedicalClassifier()
                                except Exception as reload_error:
                                    st.warning("⚠️ Please refresh the page to reload models.")
                                    st.error(f"Reload failed: {reload_error}")
                                    # Stop here if reload failed
                                    raise Exception("Cannot proceed without classifier method")
                            
                            # Call the classification method
                            results = st.session_state.classifier.classify_brain_tumor(
                                image_path=image,
                                generate_report=generate_report
                            )
                            st.session_state.last_results = results
                            st.success("✅ Brain MRI analysis complete!")
                            
                            # Show model used
                            if "model_used" in results:
                                st.info(f"**Models Used:** {results['model_used']}")
                            
                            # Show YOUR CUSTOM MODEL results prominently (PRIMARY)
                            if "brain_tumor" in results.get("classifications", {}):
                                brain_result = results["classifications"]["brain_tumor"]
                                if "error" not in brain_result:
                                    st.success(f"**🎯 PRIMARY RESULT (Your Custom Models):** {brain_result.get('disease', 'N/A')} ({brain_result.get('confidence', 0):.1%} confidence)")
                                    st.caption("This is from YOUR custom trained models (InceptionV3 + ResNet50 ensemble)")
                                    
                                    # Show all tumor type probabilities
                                    if "predictions" in brain_result:
                                        st.markdown("**Tumor Type Probabilities (Your Models):**")
                                        tumor_probs = brain_result["predictions"]
                                        for tumor_type, prob in sorted(tumor_probs.items(), key=lambda x: x[1], reverse=True):
                                            st.progress(prob, text=f"{tumor_type}: {prob:.1%}")
                                    
                                    # Show secondary verification from LLMs (if available)
                                    st.markdown("---")
                                    st.markdown("**Secondary Verification (LLMs - Backup):**")
                                    if "medsiglip" in results.get("classifications", {}):
                                        medsiglip = results["classifications"]["medsiglip"]
                                        if "error" not in medsiglip and "top_prediction" in medsiglip:
                                            st.caption(f"MedSigLIP: {medsiglip.get('top_prediction', 'N/A')}")
                                    if "medgemma" in results.get("classifications", {}):
                                        medgemma = results["classifications"]["medgemma"]
                                        if "error" not in medgemma:
                                            medgemma_pred = medgemma.get("primary_diagnosis") or medgemma.get("disease", "N/A")
                                            st.caption(f"MedGemma: {medgemma_pred}")
                            
                            display_results(results, show_details)
                            
                            # Download options
                            if results.get("report"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.download_button(
                                        label="📥 Download Text Report",
                                        data=results["report"],
                                        file_name="brain_tumor_report.txt",
                                        mime="text/plain",
                                        width='stretch',
                                        key="dl_brain_txt"
                                    )
                                with col2:
                                    try:
                                        from report_generator import generate_pdf_report
                                        import tempfile
                                        import os
                                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                                            pdf_path = tmp.name
                                        results_pdf = results.copy()
                                        results_pdf["report_text"] = ""
                                        generate_pdf_report(results_pdf, pdf_path)
                                        with open(pdf_path, "rb") as f:
                                            pdf_data = f.read()
                                        st.download_button(
                                            label="📄 Download PDF Report",
                                            data=pdf_data,
                                            file_name="brain_tumor_report.pdf",
                                            mime="application/pdf",
                                            width='stretch',
                                            key="dl_brain_pdf"
                                        )
                                        os.unlink(pdf_path)
                                    except Exception as e:
                                        st.error(f"PDF failed: {e}")
                            
                        except Exception as e:
                            st.error(f"❌ Analysis failed: {e}")
                            import traceback
                            st.code(traceback.format_exc())
            
            except Exception as e:
                st.error(f"❌ Error loading image: {e}")
    
    with col2:
        st.markdown("### 💡 Brain Tumor Tips")
        st.markdown("""
        - **Best for**: Brain tumor detection (glioma, meningioma, pituitary)
        - **Models used**: 
          - Brain Tumor Ensemble (primary - InceptionV3 + ResNet50)
          - MedSigLIP (secondary)
          - MedGemma (tertiary)
        - **Detects**: 
          - Glioma tumor
          - Meningioma tumor
          - Pituitary tumor
          - No tumor
        - **Note**: Ensemble models from major_project-main (Kaggle trained)
        """)

# ============================================
# TAB 4: MEDICAL REPORTS (Text Analysis)
# ============================================
with tab4:
    st.markdown('<div class="section-header">📝 Medical Report Analysis</div>', unsafe_allow_html=True)
    st.markdown("**Best Models:** Text Disease Extraction (Primary) + MedGemma-27b-it")
    st.markdown("**Supported:** Blood Test Reports, CT Scan Reports, Pathology Reports, Lab Results, Clinical Notes")
    
    # File upload option
    upload_option = st.radio(
        "Input Method",
        ["📤 Upload File (PDF/TXT/DOCX)", "✍️ Enter Text Manually"],
        horizontal=True,
        key="report_input_method"
    )
    
    report_text = ""
    
    if upload_option == "📤 Upload File (PDF/TXT/DOCX)":
        uploaded_file = st.file_uploader(
            "Upload Medical Report",
            type=['pdf', 'txt', 'docx', 'doc'],
            help="Upload blood test reports, CT scan reports, pathology reports, lab results, or clinical notes",
            key="report_file"
        )
        
        if uploaded_file is not None:
            file_ext = uploaded_file.name.split('.')[-1].lower()
            
            if file_ext == 'pdf':
                try:
                    import PyPDF2
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    report_text = ""
                    for page in pdf_reader.pages:
                        report_text += page.extract_text() + "\n"
                    st.success(f"✅ PDF loaded: {len(pdf_reader.pages)} page(s)")
                except ImportError:
                    st.error("❌ PyPDF2 not installed. Install with: pip install PyPDF2")
                    st.info("Falling back to text extraction...")
                    report_text = str(uploaded_file.read(), errors='ignore')
                except Exception as e:
                    st.warning(f"⚠️ PDF parsing failed: {e}. Trying text extraction...")
                    uploaded_file.seek(0)
                    report_text = str(uploaded_file.read(), errors='ignore')
            elif file_ext in ['txt', 'doc', 'docx']:
                try:
                    if file_ext == 'docx':
                        try:
                            from docx import Document
                            doc = Document(uploaded_file)
                            report_text = "\n".join([para.text for para in doc.paragraphs])
                            st.success("✅ DOCX loaded successfully")
                        except ImportError:
                            st.error("❌ python-docx not installed. Install with: pip install python-docx")
                            report_text = str(uploaded_file.read(), errors='ignore')
                        except Exception as e:
                            st.warning(f"⚠️ DOCX parsing failed: {e}. Trying text extraction...")
                            uploaded_file.seek(0)
                            report_text = str(uploaded_file.read(), errors='ignore')
                    else:
                        report_text = str(uploaded_file.read(), encoding='utf-8', errors='ignore')
                        st.success("✅ Text file loaded successfully")
                except Exception as e:
                    st.error(f"❌ Error reading file: {e}")
                    report_text = ""
            
            if report_text:
                st.text_area(
                    "Extracted Report Text (editable)",
                    value=report_text,
                    height=200,
                    key="report_text_uploaded"
                )
                report_text = st.session_state.get("report_text_uploaded", report_text)
    else:
        report_text = st.text_area(
            "Enter Medical Report Text",
            height=200,
            placeholder="""Example:
Patient presents with acute chest pain and shortness of breath.
Chest X-ray shows bilateral lower lobe opacities consistent with pneumonia.
No pneumothorax or pleural effusion noted.
Cardiomegaly is present.

Or paste blood test results, CT scan reports, pathology reports, etc.""",
            key="report_text"
        )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("🔍 Analyze Medical Report", type="primary", use_container_width=True, key="analyze_report"):
            if not report_text.strip():
                st.warning("⚠️ Please enter a medical report")
            else:
                with st.spinner("Analyzing medical report..."):
                    # Initialize classifier
                    if st.session_state.classifier is None:
                        try:
                            import importlib
                            import medical_classifier
                            importlib.reload(medical_classifier)
                            from medical_classifier import MedicalClassifier
                            st.session_state.classifier = MedicalClassifier()
                            st.success("✅ Models loaded successfully!")
                        except Exception as e:
                            st.error(f"❌ Failed to load classifier: {e}")
                            st.code(traceback.format_exc())
                            st.warning("⚠️ App will continue but some features may not work. Please refresh the page.")
                    
                    # Run text analysis
                    try:
                        # Use MedGemma for text + disease extraction
                        if not hasattr(st.session_state.classifier, 'classify_text_report'):
                            st.error("❌ classify_text_report method not found. Please restart the app.")
                            st.warning("⚠️ Please refresh the page to reload models.")
                        
                        results = st.session_state.classifier.classify_text_report(
                            report_text=report_text,
                            generate_report=generate_report
                        )
                        st.session_state.last_results = results
                        st.success("✅ Report analysis complete!")
                        
                        # Show model used
                        if "model_used" in results:
                            st.info(f"**Models Used:** {results['model_used']}")
                        
                        display_results(results, show_details)
                        
                        # Download options
                        if results.get("report"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.download_button(
                                    label="📥 Download Text Report",
                                    data=results["report"],
                                    file_name="medical_report_analysis.txt",
                                    mime="text/plain",
                                    width='stretch',
                                    key="dl_text_txt"
                                )
                            with col2:
                                try:
                                    from report_generator import generate_pdf_report
                                    import tempfile
                                    import os
                                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                                        pdf_path = tmp.name
                                    results_pdf = results.copy()
                                    results_pdf["report_text"] = report_text
                                    generate_pdf_report(results_pdf, pdf_path)
                                    with open(pdf_path, "rb") as f:
                                        pdf_data = f.read()
                                    st.download_button(
                                        label="📄 Download PDF Report",
                                        data=pdf_data,
                                        file_name="medical_report_analysis.pdf",
                                        mime="application/pdf",
                                        width='stretch',
                                        key="dl_text_pdf"
                                    )
                                    os.unlink(pdf_path)
                                except Exception as e:
                                    st.error(f"PDF failed: {e}")
                        
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {e}")
                        st.code(traceback.format_exc())
                        st.warning("⚠️ The app is still running. Please try again or refresh the page.")
                        if 'error_count' in st.session_state:
                            st.session_state.error_count += 1
                        else:
                            st.session_state.error_count = 1
    
    with col2:
        st.markdown("### 📋 Sample Reports")
        if st.button("📄 Load Sample 1", key="sample1"):
            st.session_state.sample_text = """Patient presents with acute chest pain and shortness of breath.
Chest X-ray shows bilateral lower lobe opacities consistent with pneumonia.
No pneumothorax or pleural effusion noted.
Cardiomegaly is present."""
            st.rerun()
        
        if st.button("📄 Load Sample 2", key="sample2"):
            st.session_state.sample_text = """Patient with history of smoking, presenting with cough and fever.
Radiographic findings show right upper lobe consolidation.
Possible tuberculosis or bacterial pneumonia."""
            st.rerun()
        
        if 'sample_text' in st.session_state:
            report_text = st.session_state.sample_text

# ============================================
# TAB 5: GENERAL ANALYSIS (All Types)
# ============================================
with tab5:
    st.markdown('<div class="section-header">🔬 General Medical Analysis</div>', unsafe_allow_html=True)
    st.markdown("**Best Models:** MedSigLIP (Primary) + MedGemma-27b-it")
    
    analysis_type = st.radio(
        "Select Analysis Type",
        ["Medical Image", "Medical Text", "Both Image and Text"],
        horizontal=True
    )
    
    image = None
    text = None
    
    if analysis_type in ["Medical Image", "Both Image and Text"]:
        uploaded_file = st.file_uploader(
            "Upload Medical Image",
            type=['png', 'jpg', 'jpeg', 'dcm'],
            help="Any medical image type",
            key="general_image"
        )
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Medical Image", use_container_width=True)
    
    if analysis_type in ["Medical Text", "Both Image and Text"]:
        text = st.text_area(
            "Enter Medical Information",
            height=150,
            placeholder="Enter medical report, symptoms, or clinical notes...",
            key="general_text"
        )
    
    if st.button("🔍 Run Comprehensive Analysis", type="primary", use_container_width=True, key="analyze_general"):
        if not image and not text:
            st.warning("⚠️ Please provide image or text input")
        else:
            with st.spinner("Running comprehensive analysis with all models..."):
                # Initialize classifier
                if st.session_state.classifier is None:
                    try:
                        from medical_classifier import MedicalClassifier
                        st.session_state.classifier = MedicalClassifier()
                        st.success("✅ Models loaded successfully!")
                    except Exception as e:
                        st.error(f"❌ Failed to load classifier: {e}")
                        st.warning("⚠️ Please refresh the page to reload models.")
                        # Don't stop - let user continue
                
                # Run comprehensive analysis
                try:
                    results = st.session_state.classifier.classify(
                        image_path=image if image else None,
                        report_text=text if text else None,
                        generate_report=generate_report,
                        use_comprehensive=True
                    )
                    st.session_state.last_results = results
                    st.success("✅ Comprehensive analysis complete!")
                    
                    # Show model used
                    if "model_used" in results:
                        st.info(f"**Models Used:** {results.get('model_used', 'Multiple models')}")
                    
                    display_results(results, show_details)
                    
                    # Download options
                    if results.get("report"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(
                                label="📥 Download Text Report",
                                data=results["report"],
                                file_name="comprehensive_analysis_report.txt",
                                mime="text/plain",
                                width='stretch',
                                key="dl_general_txt"
                            )
                        with col2:
                            try:
                                from report_generator import generate_pdf_report
                                import tempfile
                                import os
                                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                                    pdf_path = tmp.name
                                results_pdf = results.copy()
                                results_pdf["report_text"] = text if text else ""
                                generate_pdf_report(results_pdf, pdf_path)
                                with open(pdf_path, "rb") as f:
                                    pdf_data = f.read()
                                st.download_button(
                                    label="📄 Download PDF Report",
                                    data=pdf_data,
                                    file_name="comprehensive_analysis_report.pdf",
                                    mime="application/pdf",
                                    width='stretch',
                                    key="dl_general_pdf"
                                )
                                os.unlink(pdf_path)
                            except Exception as e:
                                st.error(f"PDF failed: {e}")
                    
                except Exception as e:
                    st.error(f"❌ Analysis failed: {e}")
                    import traceback
                    st.code(traceback.format_exc())

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>Specialized Medical Disease Classification System | Using MedGemma-27b-it & MedSigLIP</p>
</div>
""", unsafe_allow_html=True)

