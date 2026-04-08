import h5py
import json
import os

def check_h5(filepath):
    print(f"Checking {filepath}...")
    with h5py.File(filepath, "r") as f:
        config_str = f.attrs.get("model_config")
        if not config_str:
            print("No model_config")
            return
        if isinstance(config_str, bytes):
            config_str = config_str.decode("utf-8")
        
        # Look for the characteristic serialized string shapes like '"(None, 224, 224, 3)"'
        if '"(None,' in config_str or '"[' in config_str:
            print("Possible serialized string shapes found.")

if __name__ == "__main__":
    check_h5("major_project-main/models/inception_model.h5")
    check_h5("major_project-main/models/resnet_model.h5")
