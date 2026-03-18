"""
Quick Start Script for Medical Disease Classification
This script provides an easy way to test the system
"""

import os
import sys
from medical_classifier import MedicalClassifier
import json

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def main():
    print_header("Medical Disease Classification System - Quick Start")
    
    print("\nThis system can classify diseases from:")
    print("  1. Medical images (X-rays, CT scans, etc.)")
    print("  2. Medical report text")
    print("  3. Both image and text combined")
    
    # Initialize classifier
    print("\nInitializing classifier and loading models...")
    print("(This may take a few minutes on first run)")
    try:
        classifier = MedicalClassifier()
        print("\n✓ System ready!")
    except Exception as e:
        print(f"\n✗ Error initializing: {e}")
        return
    
    # Get input type
    print("\n" + "-" * 70)
    print("Select input type:")
    print("  1. Medical Image")
    print("  2. Medical Report Text")
    print("  3. Both Image and Text")
    print("  4. Exit")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    image_path = None
    report_text = None
    
    if choice == "1" or choice == "3":
        image_path = input("\nEnter path to medical image: ").strip()
        if not os.path.exists(image_path):
            print(f"✗ Error: File not found: {image_path}")
            return
    
    if choice == "2" or choice == "3":
        print("\nEnter medical report text (press Enter twice when done):")
        lines = []
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
        report_text = "\n".join(lines).strip()
        if not report_text:
            print("✗ Error: No text provided")
            return
    
    if choice == "4":
        print("Exiting...")
        return
    
    if not image_path and not report_text:
        print("✗ Error: No input provided")
        return
    
    # Run classification
    print_header("Running Classification")
    
    try:
        results = classifier.classify(
            image_path=image_path if image_path else None,
            report_text=report_text if report_text else None,
            generate_report=True
        )
        
        # Display results
        print_header("Classification Results")
        
        # MedSigLIP results
        if "medsiglip" in results.get("classifications", {}):
            medsiglip = results["classifications"]["medsiglip"]
            if "top_prediction" in medsiglip:
                print(f"\n🔍 MedSigLIP (General Detection):")
                print(f"   Top Prediction: {medsiglip['top_prediction']}")
                if "predictions" in medsiglip:
                    print("   Confidence Scores:")
                    for disease, score in list(medsiglip["predictions"].items())[:5]:
                        print(f"     - {disease}: {score:.2%}")
        
        # CheXpert results
        if "chexpert" in results.get("classifications", {}):
            chexpert = results["classifications"]["chexpert"]
            if "top_predictions" in chexpert:
                print(f"\n🏥 CheXpert DenseNet (Common Diseases):")
                for disease, score in chexpert["top_predictions"].items():
                    print(f"   - {disease}: {score:.2%}")
        
        # CXR Foundation results
        if "cxr" in results.get("classifications", {}):
            cxr = results["classifications"]["cxr"]
            print(f"\n📊 CXR Foundation (Chest Specialized):")
            print(f"   Status: {cxr.get('note', 'Embeddings generated')}")
        
        # Generated report
        if results.get("report"):
            print_header("Generated Radiology Report")
            print(results["report"])
        
        # Save results
        save = input("\n\nSave results to file? (y/n): ").strip().lower()
        if save == "y":
            output_file = "classification_results.json"
            with open(output_file, "w") as f:
                json.dump(results, f, indent=2)
            print(f"✓ Results saved to {output_file}")
        
    except Exception as e:
        print(f"\n✗ Error during classification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

