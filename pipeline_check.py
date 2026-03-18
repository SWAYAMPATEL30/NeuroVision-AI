from medical_classifier import MedicalClassifier
from PIL import Image
from report_generator import generate_pdf_report
import tempfile
import os
import json


def main():
    print("Initializing classifier...")
    classifier = MedicalClassifier()

    blank = Image.new("RGB", (224, 224), "white")
    summary = {}

    # Chest X-ray
    print("\n[1] Chest X-ray pipeline test")
    chest = classifier.classify_chest_xray(blank, generate_report=True)
    summary["chest"] = {
        "best_prediction": chest.get("best_prediction", {}).get("disease"),
        "report_generated": bool(chest.get("report")),
        "errors": chest.get("error"),
    }
    print("  Best prediction:", summary["chest"]["best_prediction"])
    print("  Report generated:", summary["chest"]["report_generated"])
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf_path = tmp.name
    try:
        generate_pdf_report(chest, pdf_path)
        summary["chest"]["pdf_ok"] = True
        print("  PDF generation: OK ->", pdf_path)
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    # Bone X-ray
    print("\n[2] Bone X-ray pipeline test")
    bone = classifier.classify_bone_xray(blank, generate_report=True)
    summary["bone"] = {
        "best_prediction": bone.get("best_prediction", {}).get("disease"),
        "report_generated": bool(bone.get("report")),
        "errors": bone.get("error"),
    }
    print("  Best prediction:", summary["bone"]["best_prediction"])
    print("  Report generated:", summary["bone"]["report_generated"])
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf_path = tmp.name
    try:
        generate_pdf_report(bone, pdf_path)
        summary["bone"]["pdf_ok"] = True
        print("  PDF generation: OK ->", pdf_path)
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    # Text report
    print("\n[3] Medical text report pipeline test")
    text_input = (
        "Patient presents with persistent cough and pneumonia findings on recent scan. "
        "No fracture."
    )
    text_res = classifier.classify_text_report(text_input, generate_report=True)
    summary["text"] = {
        "best_prediction": text_res.get("best_prediction", {}).get("disease"),
        "report_generated": bool(text_res.get("report")),
        "extracted": text_res.get("extracted_diseases", {}).get("diseases", []),
    }
    print("  Best prediction:", summary["text"]["best_prediction"])
    print("  Report generated:", summary["text"]["report_generated"])
    print("  Extracted diseases:", summary["text"]["extracted"][:3])
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf_path = tmp.name
    try:
        generate_pdf_report(text_res, pdf_path)
        summary["text"]["pdf_ok"] = True
        print("  PDF generation: OK ->", pdf_path)
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    print("\nSummary:")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

