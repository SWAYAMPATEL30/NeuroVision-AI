"""
Convert brain tumor models to compatible format
"""

import tensorflow as tf
import os

print("Converting brain tumor models to compatible format...")

inception_path = "major_project-main/models/inception_model.h5"
resnet_path = "major_project-main/models/resnet_model.h5"

# Try to load and save with current TensorFlow version
try:
    print("\n1. Converting InceptionV3 model...")
    if os.path.exists(inception_path):
        # Try loading with legacy format
        try:
            model = tf.keras.models.load_model(inception_path, compile=False)
            # Save in new format
            new_path = inception_path.replace('.h5', '_compatible.h5')
            model.save(new_path, save_format='h5')
            print(f"   [OK] Saved compatible version: {new_path}")
        except Exception as e:
            print(f"   [INFO] Direct conversion failed: {e}")
            print("   Will use fallback loading method at runtime")
    else:
        print(f"   [MISSING] {inception_path}")
    
    print("\n2. Converting ResNet50 model...")
    if os.path.exists(resnet_path):
        try:
            model = tf.keras.models.load_model(resnet_path, compile=False)
            new_path = resnet_path.replace('.h5', '_compatible.h5')
            model.save(new_path, save_format='h5')
            print(f"   [OK] Saved compatible version: {new_path}")
        except Exception as e:
            print(f"   [INFO] Direct conversion failed: {e}")
            print("   Will use fallback loading method at runtime")
    else:
        print(f"   [MISSING] {resnet_path}")
    
    print("\n[INFO] Models will be loaded with compatibility fallback at runtime")
    print("The system will automatically rebuild models if needed")
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    print("\n[INFO] Models will use runtime compatibility handling")


