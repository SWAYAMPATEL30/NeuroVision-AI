"""
PDF Report Generator for Medical Classification Results
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import json

def generate_pdf_report(results: dict, output_path: str = "radiology_report.pdf"):
    """You are a clinical documentation specialist. Generate a structured, professional medical report , from the provided classification results and clinical findings.

The report must include:
- Findings
- Impression / Diagnosis
- Confidence Level
- Recommendations

Use formal clinical language, flag urgent findings with [URGENT], 
and end with: "This is AI-assisted and must be reviewed by a 
licensed physician before clinical use."""
    
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=6
    )
    
    # Title
    elements.append(Paragraph("RADIOLOGY REPORT", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Report metadata
    report_date = datetime.now().strftime("%B %d, %Y")
    elements.append(Paragraph(f"<b>Report Date:</b> {report_date}", normal_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Clinical Indication
    elements.append(Paragraph("CLINICAL INDICATION", heading_style))
    if results.get("report_text"):
        elements.append(Paragraph(results["report_text"], normal_style))
    else:
        elements.append(Paragraph("Clinical indication not provided.", normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Model Results Section
    elements.append(Paragraph("AI MODEL ANALYSIS RESULTS", heading_style))
    
    classifications = results.get("classifications", {})
    
    # MedSigLIP Results
    if "medsiglip" in classifications and "error" not in classifications["medsiglip"]:
        medsiglip = classifications["medsiglip"]
        elements.append(Paragraph("<b>MedSigLIP (General Detection):</b>", normal_style))
        if "top_prediction" in medsiglip:
            pred = medsiglip["top_prediction"]
            conf = medsiglip.get("predictions", {}).get(pred, 0)
            elements.append(Paragraph(f"Primary Prediction: {pred} (Confidence: {conf:.1%})", normal_style))
        if "predictions" in medsiglip:
            sorted_preds = sorted(medsiglip["predictions"].items(), key=lambda x: x[1], reverse=True)[:5]
            pred_text = "Top Predictions: " + ", ".join([f"{d} ({s:.1%})" for d, s in sorted_preds])
            elements.append(Paragraph(pred_text, normal_style))
        elements.append(Spacer(1, 0.1*inch))
    
    # CheXpert Results
    if "chexpert" in classifications and "error" not in classifications["chexpert"]:
        chexpert = classifications["chexpert"]
        elements.append(Paragraph("<b>CheXpert DenseNet (High Accuracy):</b>", normal_style))
        if "top_predictions" in chexpert:
            pred_text = ", ".join([f"{d} ({s:.1%})" for d, s in list(chexpert["top_predictions"].items())[:5]])
            elements.append(Paragraph(pred_text, normal_style))
        elements.append(Spacer(1, 0.1*inch))
    
    # CXR Foundation Results
    if "cxr" in classifications and "error" not in classifications["cxr"]:
        cxr = classifications["cxr"]
        elements.append(Paragraph("<b>CXR Foundation (Chest Specialized):</b>", normal_style))
        if "top_predictions" in cxr:
            pred_text = ", ".join([f"{d} ({s:.1%})" for d, s in list(cxr["top_predictions"].items())[:3]])
            elements.append(Paragraph(pred_text, normal_style))
    # CXR Foundation Results
    if "cxr" in classifications and "error" not in classifications["cxr"]:
        cxr = classifications["cxr"]
        elements.append(Paragraph("<b>CXR Foundation (Chest Specialized):</b>", normal_style))
        if "top_predictions" in cxr:
            pred_text = ", ".join([f"{d} ({s:.1%})" for d, s in list(cxr["top_predictions"].items())[:3]])
            elements.append(Paragraph(pred_text, normal_style))
        elements.append(Spacer(1, 0.1*inch))
    
    # Brain Tumor Results
    if "brain_tumor" in classifications and "error" not in classifications["brain_tumor"]:
        brain = classifications["brain_tumor"]
        elements.append(Paragraph("<b>Brain Tumor MRI Analysis:</b>", normal_style))
        if "disease" in brain:
            elements.append(Paragraph(f"Primary Finding: {brain['disease']} (Confidence: {brain.get('confidence', 0):.1%})", normal_style))
        if "predictions" in brain:
            sorted_preds = sorted(brain["predictions"].items(), key=lambda x: x[1], reverse=True)[:5]
            pred_text = "Probabilities: " + ", ".join([f"{d} ({s:.1%})" for d, s in sorted_preds])
            elements.append(Paragraph(pred_text, normal_style))
        elements.append(Spacer(1, 0.1*inch))

    # Bone X-Ray Results
    if "bone_xray" in classifications and "error" not in classifications["bone_xray"]:
        bone = classifications["bone_xray"]
        elements.append(Paragraph("<b>Bone X-Ray Analysis:</b>", normal_style))
        if "disease" in bone:
            elements.append(Paragraph(f"Primary Finding: {bone['disease']} (Confidence: {bone.get('confidence', 0):.1%})", normal_style))
        if "predictions" in bone:
            sorted_preds = sorted(bone["predictions"].items(), key=lambda x: x[1], reverse=True)[:5]
            pred_text = "Probabilities: " + ", ".join([f"{d} ({s:.1%})" for d, s in sorted_preds])
            elements.append(Paragraph(pred_text, normal_style))
        elements.append(Spacer(1, 0.1*inch))
    
    # Extracted Diseases from Text
    if "extracted_diseases" in results and results["extracted_diseases"].get("diseases"):
        elements.append(Paragraph("<b>Diseases Extracted from Text:</b>", normal_style))
        diseases = results["extracted_diseases"]["diseases"]
        disease_list = ", ".join([f"{d['disease']} ({d.get('category', 'other')})" for d in diseases[:10]])
        elements.append(Paragraph(disease_list, normal_style))
        elements.append(Spacer(1, 0.1*inch))
    
    elements.append(Spacer(1, 0.2*inch))
    
    # Findings Section
    elements.append(Paragraph("FINDINGS", heading_style))
    
    # Get best prediction
    best_prediction = None
    best_confidence = 0.0
    best_model = None
    
    for model_name, result in classifications.items():
        if not isinstance(result, dict) or "error" in result:
            continue
        
        if "top_predictions" in result:
            top_preds = result.get("top_predictions") or {}
            if top_preds:
                top = max(top_preds.items(), key=lambda x: x[1])
                if top[1] > best_confidence:
                    best_confidence = top[1]
                    best_prediction = top[0]
                    best_model = model_name
        elif "top_prediction" in result:
            pred = result["top_prediction"]
            conf = result.get("predictions", {}).get(pred, 0)
            if conf > best_confidence:
                best_confidence = conf
                best_prediction = pred
                best_model = model_name
        elif "predictions" in result:
            # Some models only expose a predictions dict
            pred_map = result.get("predictions") or {}
            if pred_map:
                top = max(pred_map.items(), key=lambda x: x[1])
                if top[1] > best_confidence:
                    best_confidence = top[1]
                    best_prediction = top[0]
                    best_model = model_name
    
    # Fall back to classifier's best_prediction if nothing extracted above
    if not best_prediction and results.get("best_prediction"):
        bp = results["best_prediction"]
        if isinstance(bp, dict) and bp.get("disease"):
            best_prediction = bp["disease"]
            best_confidence = float(bp.get("confidence") or 0.0)
            best_model = bp.get("model", "AI Model")
    
    if best_prediction:
        findings_text = f"The AI analysis identified <b>{best_prediction}</b> as the primary finding "
        findings_text += f"with {best_confidence:.1%} confidence (from {best_model}). "
        findings_text += "Additional findings from other models are detailed above."
    else:
        findings_text = "AI model analysis completed. See detailed results above."
    
    elements.append(Paragraph(findings_text, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Impression Section
    elements.append(Paragraph("IMPRESSION", heading_style))
    
    if results.get("report"):
        # Extract impression from generated report if available
        report_text = results["report"]
        if "IMPRESSION" in report_text.upper() or "Impression" in report_text:
            # Try to extract impression section
            impression_start = report_text.upper().find("IMPRESSION")
            if impression_start != -1:
                impression_text = report_text[impression_start:impression_start+500]
                elements.append(Paragraph(impression_text, normal_style))
            else:
                elements.append(Paragraph("See detailed analysis above.", normal_style))
        else:
            elements.append(Paragraph("Based on the AI model analysis, findings are consistent with the primary prediction identified above.", normal_style))
    else:
        if best_prediction:
            elements.append(Paragraph(f"Based on comprehensive AI analysis, the findings are most consistent with <b>{best_prediction}</b> (confidence: {best_confidence:.1%}).", normal_style))
        else:
            elements.append(Paragraph("See findings section above for detailed analysis.", normal_style))
    
    elements.append(Spacer(1, 0.2*inch))
    
    # Recommendations
    elements.append(Paragraph("RECOMMENDATIONS", heading_style))
    recommendations = [
        "Clinical correlation with patient history and physical examination is recommended.",
        "Consider follow-up imaging if clinically indicated.",
        "Further diagnostic workup may be warranted based on clinical presentation."
    ]
    for rec in recommendations:
        elements.append(Paragraph(f"• {rec}", normal_style))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    elements.append(Paragraph("<i>This report was generated using AI-assisted medical image analysis. All findings should be reviewed by a qualified radiologist.</i>", 
                              ParagraphStyle('Footer', parent=normal_style, fontSize=9, textColor=colors.grey)))
    
    # Build PDF
    doc.build(elements)
    return output_path




