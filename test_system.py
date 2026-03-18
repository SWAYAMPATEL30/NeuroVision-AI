"""
Test script to verify the medical classification system works
"""

import sys
import os

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("=" * 70)
print("Medical Disease Classification System - Test")
print("=" * 70)

try:
    from medical_classifier import MedicalClassifier
    print("\n1. Module import: SUCCESS")
except Exception as e:
    print(f"\n1. Module import: FAILED - {e}")
    sys.exit(1)

try:
    print("\n2. Initializing classifier...")
    print("   (This will attempt to load models - may take a few minutes)")
    classifier = MedicalClassifier()
    print("   Classifier initialization: SUCCESS")
except Exception as e:
    print(f"   Classifier initialization: FAILED - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test with a simple example
print("\n3. Testing classification with sample text...")
try:
    sample_text = "Patient presents with chest pain and shortness of breath. Chest X-ray shows bilateral lower lobe opacities."
    results = classifier.classify(
        report_text=sample_text,
        generate_report=False  # Skip report generation for test
    )
    print("   Text classification: SUCCESS")
    print(f"   Results keys: {list(results.keys())}")
except Exception as e:
    print(f"   Text classification: FAILED - {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("System test complete!")
print("=" * 70)
print("\nNote: If models failed to load, you may need:")
print("  1. A valid Hugging Face token")
print("  2. Internet connection for model downloads")
print("  3. Sufficient disk space (~10GB)")
print("\nYou can now use the system with:")
print("  python quick_start.py")
print("  python medical_classifier.py")




