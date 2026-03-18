"""
Quick demo of the medical classification system
"""

import sys
import os

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from medical_classifier import MedicalClassifier
import json

print("=" * 70)
print("Medical Disease Classification System - Demo")
print("=" * 70)

# Initialize classifier
print("\nInitializing classifier...")
classifier = MedicalClassifier()

# Demo 1: Text-based classification
print("\n" + "-" * 70)
print("Demo 1: Classifying from Medical Report Text")
print("-" * 70)

sample_report = """
Patient presents with acute chest pain and shortness of breath.
Chest X-ray shows bilateral lower lobe opacities consistent with 
pneumonia. No pneumothorax or pleural effusion noted.
Cardiomegaly is present.
"""

print("\nSample Report:")
print(sample_report)

print("\nRunning classification...")
results = classifier.classify(
    report_text=sample_report,
    generate_report=True
)

print("\n" + "=" * 70)
print("CLASSIFICATION RESULTS")
print("=" * 70)

# Display CheXpert results
if "chexpert" in results.get("classifications", {}):
    chexpert = results["classifications"]["chexpert"]
    if "top_predictions" in chexpert:
        print("\nTop Disease Predictions (CheXpert DenseNet):")
        for disease, score in chexpert["top_predictions"].items():
            print(f"  - {disease}: {score:.1%}")

# Display MedSigLIP results if available
if "medsiglip" in results.get("classifications", {}):
    medsiglip = results["classifications"]["medsiglip"]
    if "top_prediction" in medsiglip:
        print(f"\nGeneral Detection (MedSigLIP): {medsiglip['top_prediction']}")

# Display report
if results.get("report"):
    print("\n" + "=" * 70)
    print("GENERATED RADIOLOGY REPORT")
    print("=" * 70)
    print(results["report"])

print("\n" + "=" * 70)
print("Demo Complete!")
print("=" * 70)
print("\nTo use with your own data:")
print("  python quick_start.py")
print("  python medical_classifier.py")




