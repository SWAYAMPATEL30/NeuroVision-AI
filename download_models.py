"""
Pre-download all required AI models to local directory.
Run this ONCE: python download_models.py
After this, the app runs fully offline — no runtime downloads needed.
"""

import os
import sys

# Load .env first
_ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
try:
    from dotenv import load_dotenv
    load_dotenv(_ENV_FILE, override=True)
except ImportError:
    if os.path.exists(_ENV_FILE):
        with open(_ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

HF_TOKEN = os.getenv("HF_TOKEN")

# Local cache directory — all models stored HERE in project folder
LOCAL_MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hf_models")
os.makedirs(LOCAL_MODELS_DIR, exist_ok=True)

print("=" * 60)
print("  Synapse Medical AI — Model Downloader")
print("=" * 60)
print(f"  Models will be saved to: {LOCAL_MODELS_DIR}")
print(f"  HF Token: {'✅ Found' if HF_TOKEN else '❌ Missing (some models may fail)'}")
print("=" * 60)


def download_hf_model(model_id: str, model_type: str = "auto"):
    """Download a HuggingFace model to the local models directory."""
    import shutil
    print(f"  ⬇️  Downloading: {model_id} ...")
    try:
        from transformers import AutoModel, AutoProcessor, AutoImageProcessor, CLIPModel, CLIPProcessor
        import warnings
        warnings.filterwarnings("ignore")
        os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

        kwargs = dict(
            token=HF_TOKEN,
            cache_dir=LOCAL_MODELS_DIR,
            local_files_only=False,
            trust_remote_code=True,
        )

        if model_type == "clip":
            CLIPModel.from_pretrained(model_id, **kwargs)
            CLIPProcessor.from_pretrained(model_id, cache_dir=LOCAL_MODELS_DIR, token=HF_TOKEN)
        else:
            AutoModel.from_pretrained(model_id, **kwargs)
            try:
                AutoProcessor.from_pretrained(model_id, cache_dir=LOCAL_MODELS_DIR, token=HF_TOKEN, trust_remote_code=True)
            except Exception:
                try:
                    AutoImageProcessor.from_pretrained(model_id, cache_dir=LOCAL_MODELS_DIR, token=HF_TOKEN)
                except Exception:
                    pass

        print(f"  ✅ Downloaded: {model_id} → {LOCAL_MODELS_DIR}")
        return LOCAL_MODELS_DIR
    except Exception as e:
        print(f"  ❌ Failed: {model_id} — {e}")
        return None


def main():
    results = {}

    # ── 1. CLIP (fallback for MedSigLIP) ──────────────────────────────────────
    print("\n[1/3] Downloading CLIP (openai/clip-vit-base-patch32)...")
    results["clip"] = download_hf_model("openai/clip-vit-base-patch32", model_type="clip")

    # ── 2. MedSigLIP (Medical Vision-Language Model) ──────────────────────────
    print("\n[2/3] Downloading MedSigLIP (fokan/MedSigLIP)...")
    results["medsiglip"] = download_hf_model("fokan/MedSigLIP")
    if not results["medsiglip"]:
        print("  ⚠️  MedSigLIP failed, CLIP will be used as fallback.")

    # ── 3. Swin Transformer (CXR alternative, public) ─────────────────────────
    print("\n[3/3] Downloading Swin Transformer (CXR alternative)...")
    results["swin"] = download_hf_model("microsoft/swin-tiny-patch4-window7-224")

    # ── Update medical_classifier.py to use local paths ───────────────────────
    print("\n" + "=" * 60)
    print("  Updating medical_classifier.py to use local model cache...")
    _update_classifier_cache_dir(LOCAL_MODELS_DIR)

    print("\n" + "=" * 60)
    print("  Download Summary:")
    print("=" * 60)
    for name, path in results.items():
        status = "✅" if path else "❌"
        print(f"  {status} {name}: {path or 'Not downloaded'}")

    print("\n✅ Done! The app will now load models from local disk.")
    print(f"   Location: {LOCAL_MODELS_DIR}")
    print("   Run: python api.py  (no internet needed for models)")


def _update_classifier_cache_dir(local_dir: str):
    """Update medical_classifier.py to point to the local model cache."""
    clf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "medical_classifier.py")
    if not os.path.exists(clf_path):
        print("  ⚠️  medical_classifier.py not found, skipping update.")
        return

    with open(clf_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace the cache_dir to point to local directory
    old = 'cache_dir = os.path.expanduser("~/.cache/huggingface/hub")'
    new = f'cache_dir = r"{local_dir}"  # LOCAL CACHE — set by download_models.py'

    if old in content:
        content = content.replace(old, new)
        with open(clf_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✅ Updated cache_dir in medical_classifier.py → {local_dir}")
    elif local_dir in content:
        print(f"  ✅ medical_classifier.py already uses local cache dir.")
    else:
        print("  ⚠️  Could not find cache_dir in medical_classifier.py — update manually.")


if __name__ == "__main__":
    main()
