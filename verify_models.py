"""
Script to verify all models are downloaded and working
"""

import sys
import os

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from medical_classifier import MedicalClassifier
from PIL import Image
import numpy as np

print("=" * 70)
print("Verifying All Models Are Downloaded and Working")
print("=" * 70)

# Initialize classifier
print("\n1. Initializing classifier and loading models...")
classifier = MedicalClassifier()

# Create a dummy test image
print("\n2. Creating test image...")
test_image = Image.new('RGB', (224, 224), color='white')
# Add some noise to make it more realistic
import numpy as np
img_array = np.array(test_image)
img_array = img_array + np.random.randint(0, 50, img_array.shape, dtype=np.uint8)
test_image = Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))

print("\n3. Testing each model individually...")
print("-" * 70)

# Test MedSigLIP
print("\n[1] Testing MedSigLIP...")
if classifier.models.get('medsiglip') is not None:
    try:
        result = classifier.classify_with_medsiglip(test_image)
        if "error" not in result:
            print(f"   ✓ SUCCESS - Top prediction: {result.get('top_prediction', 'N/A')}")
            print(f"   Predictions: {list(result.get('predictions', {}).keys())[:3]}")
        else:
            print(f"   ✗ FAILED - {result.get('error')}")
    except Exception as e:
        print(f"   ✗ FAILED - {e}")
else:
    print("   ✗ Model not loaded")

# Test CXR Foundation
print("\n[2] Testing CXR Foundation...")
if classifier.models.get('cxr') is not None:
    try:
        result = classifier.classify_with_cxr(test_image)
        if "error" not in result:
            print(f"   ✓ SUCCESS - Model: {result.get('model', 'N/A')}")
            if "top_predictions" in result:
                print(f"   Top predictions: {list(result['top_predictions'].keys())[:3]}")
            else:
                print(f"   Embeddings shape: {result.get('embeddings_shape', 'N/A')}")
        else:
            print(f"   ✗ FAILED - {result.get('error')}")
    except Exception as e:
        print(f"   ✗ FAILED - {e}")
else:
    print("   ✗ Model not loaded")

# Test CheXpert
print("\n[3] Testing CheXpert DenseNet...")
if classifier.models.get('chexpert') is not None:
    try:
        result = classifier.classify_with_chexpert(test_image)
        if "error" not in result:
            print(f"   ✓ SUCCESS - Model: {result.get('model', 'N/A')}")
            if "top_predictions" in result:
                print(f"   Top predictions: {list(result['top_predictions'].keys())[:3]}")
        else:
            print(f"   ✗ FAILED - {result.get('error')}")
    except Exception as e:
        print(f"   ✗ FAILED - {e}")
else:
    print("   ✗ Model not loaded")

# Test full classification pipeline
print("\n" + "-" * 70)
print("\n4. Testing full classification pipeline...")
try:
    results = classifier.classify(
        image_path=test_image,
        generate_report=False  # Skip report to test models only
    )
    
    print("\nClassification Results Summary:")
    print("-" * 70)
    
    model_outputs = 0
    for model_name, result in results.get("classifications", {}).items():
        if "error" not in result:
            model_outputs += 1
            print(f"\n{model_name.upper()}:")
            if "top_predictions" in result:
                print(f"  Top predictions: {list(result['top_predictions'].keys())[:3]}")
            elif "top_prediction" in result:
                print(f"  Top prediction: {result['top_prediction']}")
            elif "predictions" in result:
                print(f"  Predictions available: {len(result['predictions'])} diseases")
    
    print(f"\n✓ Models generating outputs: {model_outputs}/{len(results.get('classifications', {}))}")
    
except Exception as e:
    print(f"✗ Pipeline test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("Verification Complete!")
print("=" * 70)
print("\nKey Points:")
print("  - All classifications come from Hugging Face models")
print("  - Groq API is used ONLY for report generation (backup)")
print("  - Models must be downloaded and working for classifications")




