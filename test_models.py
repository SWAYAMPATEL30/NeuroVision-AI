"""
Test script to verify models are working correctly
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

print("=" * 60)
print("Testing Medical Classification Models")
print("=" * 60)

try:
    from medical_classifier import MedicalClassifier
    
    print("\n1. Initializing classifier...")
    classifier = MedicalClassifier()
    
    print("\n2. Checking loaded models...")
    loaded_models = []
    for name, model in classifier.models.items():
        if model is not None:
            loaded_models.append(name)
            print(f"   [OK] {name}")
        else:
            print(f"   [FAILED] {name}")
    
    if not loaded_models:
        print("\n[ERROR] No models loaded!")
        sys.exit(1)
    
    print(f"\n3. Loaded {len(loaded_models)}/{len(classifier.models)} models")
    
    # Create a test image (simple white image)
    print("\n4. Creating test image...")
    test_image = Image.new('RGB', (224, 224), color='white')
    
    print("\n5. Testing MedSigLIP...")
    if classifier.models.get('medsiglip') is not None:
        test_prompts = ["pneumonia", "fracture", "normal", "tumor"]
        result = classifier.classify_with_medsiglip(test_image, text_prompts=test_prompts, use_comprehensive=False)
        print(f"   Result: {result}")
        if "error" in result:
            print(f"   [ERROR] {result['error']}")
        elif "predictions" in result:
            print(f"   [OK] Got {len(result['predictions'])} predictions")
            print(f"   Top prediction: {result.get('top_prediction', 'N/A')}")
            print(f"   Predictions: {result['predictions']}")
    else:
        print("   [SKIP] MedSigLIP not loaded")
    
    print("\n6. Testing CheXpert...")
    if classifier.models.get('chexpert') is not None:
        result = classifier.classify_with_chexpert(test_image)
        print(f"   Result keys: {list(result.keys())}")
        if "error" in result:
            print(f"   [ERROR] {result['error']}")
        elif "top_predictions" in result:
            print(f"   [OK] Got {len(result['top_predictions'])} top predictions")
            print(f"   Top predictions: {result['top_predictions']}")
    else:
        print("   [SKIP] CheXpert not loaded")
    
    print("\n7. Testing CXR Foundation...")
    if classifier.models.get('cxr') is not None:
        result = classifier.classify_with_cxr(test_image)
        print(f"   Result keys: {list(result.keys())}")
        if "error" in result:
            print(f"   [ERROR] {result['error']}")
        elif "top_predictions" in result:
            print(f"   [OK] Got {len(result['top_predictions'])} top predictions")
            print(f"   Top predictions: {result['top_predictions']}")
    else:
        print("   [SKIP] CXR Foundation not loaded")
    
    print("\n8. Testing get_best_model_prediction...")
    test_results = {}
    if classifier.models.get('medsiglip') is not None:
        medsiglip_result = classifier.classify_with_medsiglip(test_image, text_prompts=["pneumonia", "fracture", "normal"], use_comprehensive=False)
        test_results["medsiglip"] = medsiglip_result
    
    # Add CheXpert results
    if classifier.models.get('chexpert') is not None:
        chexpert_result = classifier.classify_with_chexpert(test_image)
        test_results["chexpert"] = chexpert_result
        print(f"   CheXpert added to test: {chexpert_result.get('top_predictions', {})}")
    
    best = classifier.get_best_model_prediction(test_results)
    print(f"   Best prediction: {best}")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n[ERROR] Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

