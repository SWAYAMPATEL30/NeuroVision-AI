"""
Script to download all medical models in advance
This can be run separately to download models before first use
"""

from huggingface_hub import login, snapshot_download
import os

# Hugging Face token
HF_TOKEN = os.getenv("HF_TOKEN")

# Login to Hugging Face
print("Logging in to Hugging Face...")
login(token=HF_TOKEN)

# Models to download
models = {
    "MedSigLIP": "fokan/MedSigLIP",
    "CXR Foundation": "google/cxr-foundation",
}

print("\n" + "=" * 60)
print("Downloading Medical Models")
print("=" * 60)

for model_name, model_id in models.items():
    print(f"\nDownloading {model_name} ({model_id})...")
    try:
        snapshot_download(
            repo_id=model_id,
            token=HF_TOKEN,
            local_dir=f"./models/{model_id.replace('/', '_')}",
            local_dir_use_symlinks=False
        )
        print(f"✓ {model_name} downloaded successfully")
    except Exception as e:
        print(f"✗ Failed to download {model_name}: {e}")

print("\n" + "=" * 60)
print("Model download complete!")
print("=" * 60)
print("\nNote: CheXpert DenseNet uses PyTorch's torchvision models")
print("and will be downloaded automatically when first used.")




