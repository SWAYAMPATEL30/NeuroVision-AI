"""
Test script for brain tumor model integration
"""

import sys
import os
from PIL import Image
import numpy as np

# Fix encoding
if sys.platform == 'win32':
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("=" * 70)
print("Testing Brain Tumor Model Integration")
print("=" * 70)

# Check if models exist
print("\n1. Checking model files...")
model_paths = [
    "major_project-main/models/inception_model.h5",
    "major_project-main/models/resnet_model.h5"
]

models_found = []
for path in model_paths:
    if os.path.exists(path):
        print(f"   [OK] {path}")
        models_found.append(path)
    else:
        print(f"   [MISSING] {path}")

if not models_found:
    print("\n[ERROR] No brain tumor models found!")
    print("Please ensure models are extracted to major_project-main/models/")
    sys.exit(1)

# Test classifier initialization
print("\n2. Initializing MedicalClassifier...")
try:
    from medical_classifier import MedicalClassifier
    classifier = MedicalClassifier()
    print("   [OK] Classifier initialized")
except Exception as e:
    print(f"   [ERROR] Failed to initialize: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Check if brain tumor models loaded
print("\n3. Checking brain tumor models...")
if classifier.models.get('brain_tumor') is not None:
    brain_models = classifier.models['brain_tumor']
    print(f"   [OK] Loaded {len(brain_models)} brain tumor model(s)")
    for name, model in brain_models:
        print(f"      - {name}")
    print(f"   [OK] Class labels: {classifier.brain_tumor_labels}")
else:
    print("   [WARNING] Brain tumor models not loaded")
    print("   Will use fallback models (MedSigLIP, MedGemma)")

# Create test image
print("\n4. Creating test image...")
test_image = Image.new('RGB', (224, 224), color=(128, 128, 128))
# Add some variation
img_array = np.array(test_image)
img_array = img_array + np.random.randint(-20, 20, img_array.shape, dtype=np.int16)
img_array = np.clip(img_array, 0, 255).astype(np.uint8)
test_image = Image.fromarray(img_array)
print("   [OK] Test image created (224x224)")

# Test classification
print("\n5. Testing brain tumor classification...")
try:
    results = classifier.classify_brain_tumor(
        image_path=test_image,
        generate_report=False
    )
    
    print("   [OK] Classification completed")
    print(f"\n   Results:")
    print(f"   - Input type: {results.get('input_type')}")
    print(f"   - Model used: {results.get('model_used')}")
    
    if "brain_tumor" in results.get("classifications", {}):
        brain_result = results["classifications"]["brain_tumor"]
        if "error" not in brain_result:
            print(f"\n   Brain Tumor Model Results:")
            print(f"   - Model: {brain_result.get('model')}")
            print(f"   - Top prediction: {brain_result.get('top_prediction')}")
            print(f"   - Confidence: {brain_result.get('top_confidence', 0):.1%}")
            print(f"   - All predictions:")
            for label, conf in brain_result.get("predictions", {}).items():
                print(f"     * {label}: {conf:.1%}")
        else:
            print(f"   [ERROR] {brain_result.get('error')}")
    
    if "best_prediction" in results:
        best = results["best_prediction"]
        print(f"\n   Best Prediction:")
        print(f"   - Model: {best.get('model')}")
        print(f"   - Disease: {best.get('disease')}")
        print(f"   - Confidence: {best.get('confidence', 0):.1%}")
    
    print("\n" + "=" * 70)
    print("[SUCCESS] Brain tumor integration test passed!")
    print("=" * 70)
    
except Exception as e:
    print(f"   [ERROR] Classification failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


