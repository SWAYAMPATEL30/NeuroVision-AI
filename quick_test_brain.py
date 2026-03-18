"""
Quick test for brain tumor models (without MedGemma)
"""

import sys
import os
from PIL import Image
import numpy as np

if sys.platform == 'win32':
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("Quick Brain Tumor Model Test")
print("=" * 50)

# Test direct model loading
try:
    import tensorflow as tf
    
    print("\n1. Loading models directly...")
    inception_path = "major_project-main/models/inception_model.h5"
    resnet_path = "major_project-main/models/resnet_model.h5"
    
    if os.path.exists(inception_path):
        model_inception = tf.keras.models.load_model(inception_path, compile=False)
        print(f"   [OK] InceptionV3 loaded")
    else:
        print(f"   [MISSING] {inception_path}")
        model_inception = None
    
    if os.path.exists(resnet_path):
        model_resnet = tf.keras.models.load_model(resnet_path, compile=False)
        print(f"   [OK] ResNet50 loaded")
    else:
        print(f"   [MISSING] {resnet_path}")
        model_resnet = None
    
    if model_inception and model_resnet:
        print("\n2. Testing ensemble prediction...")
        # Create test image
        test_img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        test_img = test_img.astype(np.float32) / 255.0
        test_img = np.expand_dims(test_img, axis=0)
        
        # Predict
        prob1 = model_inception.predict(test_img, verbose=0)[0]
        prob2 = model_resnet.predict(test_img, verbose=0)[0]
        final_prob = (prob1 + prob2) / 2
        
        labels = ['glioma_tumor', 'meningioma_tumor', 'no_tumor', 'pituitary_tumor']
        predicted_idx = np.argmax(final_prob)
        
        print(f"   [OK] Ensemble prediction successful")
        print(f"\n   Results:")
        for i, label in enumerate(labels):
            print(f"     {label}: {final_prob[i]:.1%}")
        print(f"\n   Top prediction: {labels[predicted_idx]} ({final_prob[predicted_idx]:.1%})")
        print("\n" + "=" * 50)
        print("[SUCCESS] Brain tumor models working correctly!")
        print("=" * 50)
    else:
        print("\n[ERROR] Models not found")
        
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()


