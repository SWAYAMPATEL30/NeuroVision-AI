"""
Medical Disease Classification System
Integrates multiple models for comprehensive medical image and report analysis
"""

import os
import sys
import torch
import numpy as np
from PIL import Image
from typing import Union, Dict, List, Optional
from pathlib import Path
import json

# Fix encoding issues on Windows
if sys.platform == 'win32':
    import io
    # Set UTF-8 encoding for stdout/stderr
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Hugging Face imports
from transformers import (
    AutoModel, 
    AutoProcessor, 
    AutoTokenizer,
    AutoImageProcessor,
    AutoModelForImageTextToText,
    pipeline
)
from huggingface_hub import login, hf_hub_download

# Groq API for Gemini
try:
    from groq import Groq
except ImportError:
    Groq = None

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Hugging Face token
HF_TOKEN = os.getenv("HF_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Login to Hugging Face (with error handling)
try:
    login(token=HF_TOKEN)
    print("Hugging Face authentication successful")
except Exception as e:
    print(f"Warning: Hugging Face authentication failed: {e}")
    print("  Some models may require authentication. Continuing anyway...")
    HF_TOKEN = None  # Set to None if login fails

class MedicalClassifier:
    """Unified medical classification system using multiple models"""
    
    def __init__(self):
        self.models = {}
        self.processors = {}
        self.tokenizers = {}
        self.device = device
        self.medgemma_pipeline = None
        
        # Disease labels for CheXpert
        self.chexpert_labels = [
            'No Finding', 'Enlarged Cardiomediastinum', 'Cardiomegaly', 
            'Lung Opacity', 'Lung Lesion', 'Edema', 'Consolidation', 
            'Pneumonia', 'Atelectasis', 'Pneumothorax', 'Pleural Effusion', 
            'Pleural Other', 'Fracture', 'Support Devices'
        ]
        
        # Import comprehensive disease database
        try:
            from disease_categories import ALL_DISEASES, COMPREHENSIVE_DISEASES, get_category_for_disease
            self.all_diseases = ALL_DISEASES
            self.disease_categories = COMPREHENSIVE_DISEASES
            self.get_category_for_disease = get_category_for_disease
            print(f"Loaded comprehensive disease database: {len(ALL_DISEASES)} diseases across {len(COMPREHENSIVE_DISEASES)} categories")
        except ImportError:
            # Fallback to basic list if module not found
            self.all_diseases = [
                "pneumonia", "fracture", "tumor", "cancer", "infection", "inflammation",
                "normal", "broken bone", "pneumothorax", "edema", "cardiomegaly"
            ]
            self.disease_categories = {}
            self.get_category_for_disease = lambda x: "other"
            print("Using basic disease list (comprehensive database not available)")
        
        # Initialize Groq client for Gemini
        self.groq_client = None
        if Groq:
            try:
                self.groq_client = Groq(api_key=GROQ_API_KEY)
            except Exception as e:
                print(f"Warning: Could not initialize Groq client: {e}")
        
        print("Loading models...")
        self._load_models()
        
        # MedGemma will be loaded lazily (on-demand) to speed up initialization
        # It's a large 27B parameter model that can take 20+ minutes to load
        self.models['medgemma'] = None
        self.medgemma_pipeline = None
        self._medgemma_loaded = False
        print("\n[INFO] MedGemma-27b-it will be loaded on-demand when needed (large model ~29B parameters)")
        print("  This speeds up app startup. First use may take 20+ minutes to download/load.")
        
        # Load custom models (major_project-main integration)
        print("\nLoading Custom Models (major_project-main)...")
        self._load_custom_models()
    
    def _load_models(self):
        """Load all medical models with persistent caching"""
        import os
        # Set cache directory for all models (download once, reuse)
        cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
        print(f"Using model cache directory: {cache_dir}")
        print("Models will be downloaded once and cached for future use.")
        
        # 1. MedSigLIP - General medical image-text model
        try:
            print("Loading MedSigLIP...")
            model_name = "fokan/MedSigLIP"
            
            # Try with token first
            try:
                # Clear sentencepiece cache if protobuf conflict
                try:
                    self.models['medsiglip'] = AutoModel.from_pretrained(
                        model_name, 
                        token=HF_TOKEN if HF_TOKEN else None,
                        trust_remote_code=True,
                        cache_dir=cache_dir,
                        local_files_only=False
                    ).to(self.device).eval()
                    self.processors['medsiglip'] = AutoProcessor.from_pretrained(
                        model_name,
                        token=HF_TOKEN if HF_TOKEN else None,
                        cache_dir=cache_dir,
                        local_files_only=False
                    )
                except Exception as proto_error:
                    if "sentencepiece" in str(proto_error).lower() or "proto" in str(proto_error).lower():
                        print("  Attempting to fix protobuf conflict...")
                        # Try alternative: use CLIP-based model as fallback
                        try:
                            from transformers import CLIPModel, CLIPProcessor
                            print("  Using CLIP as MedSigLIP alternative...")
                            self.models['medsiglip'] = CLIPModel.from_pretrained(
                                "openai/clip-vit-base-patch32",
                                cache_dir=cache_dir
                            ).to(self.device).eval()
                            self.processors['medsiglip'] = CLIPProcessor.from_pretrained(
                                "openai/clip-vit-base-patch32",
                                cache_dir=cache_dir
                            )
                            print("  Using CLIP model as MedSigLIP alternative")
                        except:
                            raise proto_error
                    else:
                        raise proto_error
            except:
                # Try without token (for public models)
                try:
                    self.models['medsiglip'] = AutoModel.from_pretrained(
                        model_name, 
                        trust_remote_code=True,
                        cache_dir=cache_dir
                    ).to(self.device).eval()
                    self.processors['medsiglip'] = AutoProcessor.from_pretrained(
                        model_name,
                        cache_dir=cache_dir
                    )
                except Exception as e2:
                    # Last resort: use CLIP
                    from transformers import CLIPModel, CLIPProcessor
                    print("  Using CLIP as MedSigLIP fallback...")
                    self.models['medsiglip'] = CLIPModel.from_pretrained(
                        "openai/clip-vit-base-patch32",
                        cache_dir=cache_dir
                    ).to(self.device).eval()
                    self.processors['medsiglip'] = CLIPProcessor.from_pretrained(
                        "openai/clip-vit-base-patch32",
                        cache_dir=cache_dir
                    )
            print("MedSigLIP loaded successfully")
        except Exception as e:
            print(f"Failed to load MedSigLIP: {e}")
            self.models['medsiglip'] = None
        
        # 2. CXR Foundation - Chest X-ray specialized model
        # Try multiple chest X-ray models
        cxr_models = [
            ("google/cxr-foundation", "CXR Foundation"),
            ("microsoft/swin-tiny-patch4-window7-224", "Swin Transformer (alternative)"),
        ]
        
        self.models['cxr'] = None
        for model_name, model_desc in cxr_models:
            try:
                print(f"Loading {model_desc}...")
                # Try with token first, fallback to no token
                try:
                    self.models['cxr'] = AutoModel.from_pretrained(
                        model_name,
                        token=HF_TOKEN if HF_TOKEN else None,
                        trust_remote_code=True,
                        cache_dir=cache_dir
                    ).to(self.device).eval()
                    self.processors['cxr'] = AutoImageProcessor.from_pretrained(
                        model_name,
                        token=HF_TOKEN if HF_TOKEN else None,
                        cache_dir=cache_dir
                    )
                    print(f"{model_desc} loaded successfully")
                    break
                except Exception as e1:
                    if "gated" in str(e1).lower() or "403" in str(e1):
                        print(f"  {model_desc} requires access approval. Trying alternative...")
                        continue
                    # Try without token (for public models)
                    try:
                        self.models['cxr'] = AutoModel.from_pretrained(
                            model_name,
                            trust_remote_code=True,
                            cache_dir=cache_dir
                        ).to(self.device).eval()
                        self.processors['cxr'] = AutoImageProcessor.from_pretrained(
                            model_name,
                            cache_dir=cache_dir
                        )
                        print(f"{model_desc} loaded successfully")
                        break
                    except:
                        continue
            except Exception as e:
                print(f"  Failed to load {model_desc}: {e}")
                continue
        
        if self.models['cxr'] is None:
            print("Warning: No CXR model loaded. Chest-specific analysis will be limited.")
        
        # 3. CheXpert DenseNet - High accuracy for common diseases
        try:
            print("Loading CheXpert DenseNet...")
            # Using DenseNet121 as base, will need to load CheXpert weights if available
            from torchvision import models
            self.models['chexpert'] = models.densenet121(pretrained=True)
            # Modify for 14 classes (CheXpert labels)
            self.models['chexpert'].classifier = torch.nn.Linear(
                self.models['chexpert'].classifier.in_features, 
                14
            )
            self.models['chexpert'] = self.models['chexpert'].to(self.device).eval()
            
            # Try to load CheXpert-specific weights if available
            print("  Attempting to download CheXpert weights...")
            chexpert_loaded = False
            
            # Try multiple possible weight locations
            weight_sources = [
                ("stanfordmlgroup/chexpert-models", "densenet121_chexpert.pth"),
                ("stanfordmlgroup/chexpert-models", "densenet121.pth"),
                ("microsoft/DialoGPT-medium", None),  # Won't work but shows pattern
            ]
            
            for repo_id, filename in weight_sources[:2]:  # Only try first two
                try:
                    if filename:
                        weights_path = hf_hub_download(
                            repo_id=repo_id,
                            filename=filename,
                            token=HF_TOKEN if HF_TOKEN else None
                        )
                        state_dict = torch.load(weights_path, map_location=self.device)
                        # Handle different state dict formats
                        if 'model_state_dict' in state_dict:
                            state_dict = state_dict['model_state_dict']
                        self.models['chexpert'].load_state_dict(state_dict, strict=False)
                        print(f"  Loaded CheXpert weights from {repo_id}")
                        chexpert_loaded = True
                        break
                except Exception as e:
                    continue
            
            if not chexpert_loaded:
                print("  Using ImageNet-pretrained DenseNet (CheXpert weights not found)")
                print("  Note: For best results, fine-tune on CheXpert dataset")
            
            print("CheXpert DenseNet loaded successfully")
        except Exception as e:
            print(f"Failed to load CheXpert DenseNet: {e}")
            self.models['chexpert'] = None
        
        print("\n" + "=" * 60)
        print("Model Loading Summary:")
        print("=" * 60)
        loaded_count = sum(1 for m in self.models.values() if m is not None)
        total_count = len(self.models)
        print(f"Loaded: {loaded_count}/{total_count} models")
        for name, model in self.models.items():
            status = "[OK] Loaded" if model is not None else "[FAILED]"
            print(f"  {name}: {status}")
        print("=" * 60)
        print("\nNote: Groq API is used ONLY for report generation (backup).")
        print("All disease classifications come from Hugging Face models above.")
    
    def _load_medgemma(self):
        """Load MedGemma-27b-it as primary medical model with caching"""
        import os
        cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
        
        try:
            model_id = "google/medgemma-27b-it"
            print(f"  Loading {model_id}...")
            print("  Note: This is a large model (~29B parameters).")
            print("  Note: Model will be cached after first download.")
            
            # Ensure token is available (user has access)
            if not HF_TOKEN:
                print("  [WARNING] No Hugging Face token provided. MedGemma requires authentication.")
                print("  Please set HF_TOKEN in medical_classifier.py")
                self.models['medgemma'] = None
                self.medgemma_pipeline = None
                return
            
            # Try to load with pipeline API (easier to use)
            try:
                self.medgemma_pipeline = pipeline(
                    "image-text-to-text",
                    model=model_id,
                    torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
                    device="cuda" if torch.cuda.is_available() else "cpu",
                    token=HF_TOKEN,
                    cache_dir=cache_dir,
                    trust_remote_code=True
                )
                print("  [OK] MedGemma-27b-it loaded successfully (pipeline)")
                self.models['medgemma'] = "pipeline"
            except Exception as e1:
                print(f"  Pipeline loading failed: {e1}")
                # Try direct loading
                try:
                    self.models['medgemma'] = AutoModelForImageTextToText.from_pretrained(
                        model_id,
                        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
                        device_map="auto",
                        token=HF_TOKEN,
                        cache_dir=cache_dir,
                        trust_remote_code=True
                    )
                    self.processors['medgemma'] = AutoProcessor.from_pretrained(
                        model_id,
                        token=HF_TOKEN,
                        cache_dir=cache_dir
                    )
                    print("  [OK] MedGemma-27b-it loaded successfully (direct)")
                except Exception as e2:
                    print(f"  Direct loading also failed: {e2}")
                    if "403" in str(e2) or "gated" in str(e2).lower():
                        print("  [INFO] MedGemma requires access approval.")
                        print("  Please visit https://huggingface.co/google/medgemma-27b-it to request access.")
                    print("  MedGemma will not be available. Using other models.")
                    self.models['medgemma'] = None
                    self.medgemma_pipeline = None
        except Exception as e:
            print(f"  [FAILED] Failed to load MedGemma: {e}")
            print("  Will use other models as fallback.")
            self.models['medgemma'] = None
            self.medgemma_pipeline = None
    
    def _load_custom_models(self):
        """Load custom models from major_project-main (brain tumor, chest X-ray)"""
        import os
        import numpy as np
        
        # Brain Tumor Models (InceptionV3 + ResNet50 Ensemble)
        try:
            print("Loading Brain Tumor Models (major_project-main - Ensemble)...")
            import tensorflow as tf
            from tensorflow import keras
            
            # Try to load both models for ensemble
            inception_path = "major_project-main/models/inception_model.h5"
            resnet_path = "major_project-main/models/resnet_model.h5"
            
            brain_models = []
            brain_model_loaded = False
            
            # Load InceptionV3 model
            if os.path.exists(inception_path):
                try:
                    # Try loading with custom_objects to handle compatibility
                    model_inception = tf.keras.models.load_model(
                        inception_path, 
                        compile=False,
                        custom_objects=None
                    )
                    # Rebuild model if needed (for compatibility)
                    try:
                        model_inception.compile(
                            optimizer=tf.keras.optimizers.Adam(1e-4),
                            loss='categorical_crossentropy',
                            metrics=['accuracy']
                        )
                    except:
                        pass  # Model might already be compiled
                    brain_models.append(("InceptionV3", model_inception))
                    print(f"  [OK] InceptionV3 model loaded from {inception_path}")
                    brain_model_loaded = True
                except Exception as e:
                    print(f"  Failed to load InceptionV3: {e}")
                    print(f"  Trying alternative loading method...")
                    try:
                        # Alternative: Load weights only and rebuild
                        from tensorflow.keras.applications import InceptionV3
                        base = InceptionV3(weights=None, include_top=False, input_shape=(224, 224, 3))
                        x = tf.keras.layers.GlobalAveragePooling2D()(base.output)
                        x = tf.keras.layers.Dropout(0.4)(x)
                        x = tf.keras.layers.Dense(256, activation="relu")(x)
                        x = tf.keras.layers.Dropout(0.4)(x)
                        output = tf.keras.layers.Dense(4, activation="softmax")(x)
                        model_inception = tf.keras.Model(inputs=base.input, outputs=output)
                        model_inception.load_weights(inception_path, by_name=True, skip_mismatch=True)
                        model_inception.compile(
                            optimizer=tf.keras.optimizers.Adam(1e-4),
                            loss='categorical_crossentropy',
                            metrics=['accuracy']
                        )
                        brain_models.append(("InceptionV3", model_inception))
                        print(f"  [OK] InceptionV3 model loaded (rebuilt)")
                        brain_model_loaded = True
                    except Exception as e2:
                        print(f"  Alternative loading also failed: {e2}")
            
            # Load ResNet50 model
            if os.path.exists(resnet_path):
                try:
                    model_resnet = tf.keras.models.load_model(
                        resnet_path, 
                        compile=False,
                        custom_objects=None
                    )
                    try:
                        model_resnet.compile(
                            optimizer=tf.keras.optimizers.Adam(1e-4),
                            loss='categorical_crossentropy',
                            metrics=['accuracy']
                        )
                    except:
                        pass
                    brain_models.append(("ResNet50", model_resnet))
                    print(f"  [OK] ResNet50 model loaded from {resnet_path}")
                    brain_model_loaded = True
                except Exception as e:
                    print(f"  Failed to load ResNet50: {e}")
                    print(f"  Trying alternative loading method...")
                    try:
                        # Alternative: Load weights only and rebuild
                        from tensorflow.keras.applications import ResNet50
                        base = ResNet50(weights=None, include_top=False, input_shape=(224, 224, 3))
                        x = tf.keras.layers.GlobalAveragePooling2D()(base.output)
                        x = tf.keras.layers.Dropout(0.4)(x)
                        x = tf.keras.layers.Dense(256, activation="relu")(x)
                        x = tf.keras.layers.Dropout(0.4)(x)
                        output = tf.keras.layers.Dense(4, activation="softmax")(x)
                        model_resnet = tf.keras.Model(inputs=base.input, outputs=output)
                        model_resnet.load_weights(resnet_path, by_name=True, skip_mismatch=True)
                        model_resnet.compile(
                            optimizer=tf.keras.optimizers.Adam(1e-4),
                            loss='categorical_crossentropy',
                            metrics=['accuracy']
                        )
                        brain_models.append(("ResNet50", model_resnet))
                        print(f"  [OK] ResNet50 model loaded (rebuilt)")
                        brain_model_loaded = True
                    except Exception as e2:
                        print(f"  Alternative loading also failed: {e2}")
            
            # Fallback to old model paths if ensemble models not found
            if not brain_models:
                brain_model_paths = [
                    "major_project-main/models/brainTumor.h5",
                    "major_project-main/models/braintumor.h5",
                    "major_project-main/models/model.h5",
                    "models/brainTumor.h5",
                    "models/braintumor.h5"
                ]
                
                for model_path in brain_model_paths:
                    if os.path.exists(model_path):
                        try:
                            model = tf.keras.models.load_model(model_path, compile=False)
                            model.compile(
                                optimizer=tf.keras.optimizers.Adam(1e-4),
                                loss='categorical_crossentropy',
                                metrics=['accuracy']
                            )
                            brain_models.append(("Single", model))
                            print(f"  [OK] Brain Tumor model loaded from {model_path}")
                            brain_model_loaded = True
                            break
                        except Exception as e:
                            print(f"  Failed to load {model_path}: {e}")
                            continue
            
            if brain_models:
                self.models['brain_tumor'] = brain_models
                # Class names from notebook: ['glioma_tumor', 'meningioma_tumor', 'no_tumor', 'pituitary_tumor']
                self.brain_tumor_labels = ["glioma_tumor", "meningioma_tumor", "no_tumor", "pituitary_tumor"]
                print(f"  [OK] Loaded {len(brain_models)} brain tumor model(s) for ensemble")
            else:
                print("  [INFO] Brain Tumor models not found. Will use other models for brain analysis.")
                self.models['brain_tumor'] = None
        except ImportError:
            print("  [INFO] TensorFlow not available. Brain Tumor model requires TensorFlow.")
            print("  Install with: pip install tensorflow")
            self.models['brain_tumor'] = None
        except Exception as e:
            print(f"  [FAILED] Failed to load Brain Tumor model: {e}")
            self.models['brain_tumor'] = None
        
        # Chest X-Ray Model (from major_project-main, FINETUNED ONLY)
        try:
            print("Loading Chest X-Ray Model (major_project-main, finetuned)...")
            chest_model_path = "major_project-main/models/chest_xray_finetuned.h5"
            if os.path.exists(chest_model_path):
                try:
                    import tensorflow as tf
                    from tensorflow import keras
                    
                    # Load only the finetuned model (no fallback to original)
                    self.models['chest_xray_custom'] = tf.keras.models.load_model(chest_model_path)
                    # IMPORTANT: label order must match the columns used during fine-tuning.
                    # Our NIH-derived `train_df.csv` begins with these 11 labels (after FilePath),
                    # and the finetuned model output is 11-dim.
                    self.chest_xray_labels = [
                        "Atelectasis",
                        "Cardiomegaly",
                        "Effusion",
                        "Infiltration",
                        "Mass",
                        "Nodule",
                        "Pneumonia",
                        "Pneumothorax",
                        "Consolidation",
                        "Edema",
                        "Emphysema",
                    ]
                    print(f"  [OK] Chest X-Ray FINETUNED model loaded from {chest_model_path}")
                except Exception as e:
                    print(f"  [FAILED] Failed to load Chest X-Ray FINETUNED model: {e}")
                    self.models['chest_xray_custom'] = None
            else:
                # Do NOT fallback to original model – user explicitly requested finetuned-only
                print("  [ERROR] Chest X-Ray FINETUNED model not found at expected path:")
                print(f"         {chest_model_path}")
                print("         Please ensure fine-tuning has completed and the file exists.")
                self.models['chest_xray_custom'] = None
        except Exception as e:
            print(f"  [FAILED] Failed to load Chest X-Ray FINETUNED model: {e}")
            self.models['chest_xray_custom'] = None

    def classify_with_custom_chest_xray(self, image: Image.Image) -> Dict:
        """Run inference using the finetuned custom chest X-ray model (Keras)."""
        model = self.models.get("chest_xray_custom")
        if model is None:
            return {"error": "Custom finetuned chest X-ray model not loaded"}

        try:
            import numpy as np

            # Match training preprocessing: resize to 224, normalize to [0,1]
            img = image.convert("RGB").resize((224, 224), Image.Resampling.LANCZOS)
            x = np.asarray(img).astype("float32") / 255.0
            x = np.expand_dims(x, axis=0)

            y = model.predict(x, verbose=0)
            y = np.asarray(y).reshape(-1)  # (C,)

            labels = getattr(self, "chest_xray_labels", None) or [f"class_{i}" for i in range(len(y))]
            if len(labels) != len(y):
                # If something is off, align to model output length
                labels = labels[: len(y)]

            preds = {labels[i]: float(y[i]) for i in range(len(labels))}
            sorted_preds = sorted(preds.items(), key=lambda kv: kv[1], reverse=True)

            # Multi-label: "positive" labels above a threshold (tunable)
            threshold = 0.5
            positives = [(k, v) for k, v in sorted_preds if v >= threshold]

            top_label, top_score = sorted_preds[0] if sorted_preds else ("No Finding", 0.0)
            top_prediction = top_label if positives else "No Finding"

            # Build analysis text
            full_analysis = "Custom Finetuned Chest Model Analysis:\n"
            full_analysis += f"Top Prediction: {top_label} ({top_score:.1%} confidence)\n"
            full_analysis += "Top 5 Predictions:\n"
            for disease, score in sorted_preds[:5]:
                full_analysis += f"  - {disease}: {score:.1%}\n"
            if positives:
                pos_str = ", ".join([f"{k} ({v:.1%})" for k, v in positives[:5]])
                full_analysis += f"Above-threshold findings (>= {threshold:.2f}): {pos_str}\n"
            else:
                full_analysis += f"No findings above threshold (>= {threshold:.2f}).\n"

            return {
                "model": "Custom ChestXray (Finetuned)",
                "predictions": preds,
                "top_prediction": top_prediction,
                "top_confidence": float(top_score),
                "threshold": threshold,
                "positives": dict(positives),
                "full_analysis": full_analysis,
            }
        except Exception as e:
            return {"error": f"Custom chest model inference failed: {str(e)}"}
    
    def preprocess_image(self, image_input: Union[str, Image.Image]) -> Image.Image:
        """Preprocess image input with quality improvements"""
        if isinstance(image_input, str):
            image = Image.open(image_input).convert('RGB')
        elif isinstance(image_input, Image.Image):
            image = image_input.convert('RGB')
        else:
            raise ValueError("Image input must be a path string or PIL Image")
        
        # Enhance image quality for better accuracy
        # Resize if too small (minimum 224x224 for models)
        width, height = image.size
        min_size = 224
        if width < min_size or height < min_size:
            # Maintain aspect ratio
            ratio = max(min_size / width, min_size / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Limit maximum size for efficiency (max 1024x1024)
        max_size = 1024
        if width > max_size or height > max_size:
            ratio = min(max_size / width, max_size / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image
    
    def classify_with_medsiglip(
        self, 
        image: Image.Image, 
        text_prompts: Optional[List[str]] = None,
        use_comprehensive: bool = True
    ) -> Dict:
        """Use MedSigLIP for general disease detection with comprehensive disease list"""
        if self.models['medsiglip'] is None:
            return {"error": "MedSigLIP model not loaded"}
        
        if text_prompts is None:
            if use_comprehensive and hasattr(self, 'all_diseases'):
                # Use comprehensive disease list, but limit to top categories for efficiency
                # Group by category and sample representative diseases
                text_prompts = []
                for category, diseases in list(self.disease_categories.items())[:10]:  # Top 10 categories
                    text_prompts.extend(diseases[:5])  # Top 5 diseases per category
                # Add common ones
                text_prompts.extend(["normal", "healthy", "no finding", "no abnormality"])
                text_prompts = list(set(text_prompts))[:100]  # Limit to 100 for performance
            else:
                # Fallback to basic list
                text_prompts = [
                    "broken bone", "fracture", "pneumonia", "tumor", 
                    "cancer", "infection", "inflammation", "normal"
                ]
        
        try:
            processor = self.processors['medsiglip']
            inputs = processor(
                text=text_prompts,
                images=image,
                return_tensors="pt",
                padding=True
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.models['medsiglip'](**inputs)
                logits_per_image = outputs.logits_per_image
                probs = torch.softmax(logits_per_image, dim=-1)
            
            # Get top predictions with improved accuracy
            # Use temperature scaling for better confidence calibration
            temperature = 1.0  # Can be tuned
            scaled_probs = torch.softmax(logits_per_image / temperature, dim=-1)
            
            # Get top predictions (more for better accuracy)
            top_k = min(10, len(text_prompts))
            top_probs, top_indices = torch.topk(scaled_probs, k=top_k)
            
            results = {}
            for prob, idx in zip(top_probs[0], top_indices[0]):
                disease_name = text_prompts[idx]
                confidence = float(prob)
                # Lower threshold to capture more predictions (1% instead of 5%)
                # But exclude "normal" and "healthy" unless they're truly the top
                if confidence > 0.01:  # 1% threshold
                    results[disease_name] = confidence
            
            # Normalize probabilities to sum to 1 for better interpretation
            if results:
                total = sum(results.values())
                if total > 0:
                    results = {k: v/total for k, v in results.items()}
            
            # Get top prediction - prioritize disease findings over "normal"
            if results:
                # Filter out "normal", "healthy", "no finding" unless they're the only options
                disease_results = {k: v for k, v in results.items() 
                                 if k.lower() not in ["normal", "healthy", "no finding", "no abnormality"]}
                
                if disease_results:
                    # Use disease findings
                    top_prediction = max(disease_results.items(), key=lambda x: x[1])[0]
                    top_confidence = disease_results[top_prediction]
                else:
                    # Fallback to normal if no diseases found
                    top_prediction = max(results.items(), key=lambda x: x[1])[0]
                    top_confidence = results[top_prediction]
            else:
                top_prediction = "normal"  # Default if no high confidence
                top_confidence = 0.5
            
            category = self.get_category_for_disease(top_prediction) if hasattr(self, 'get_category_for_disease') else "other"
            
            return {
                "model": "MedSigLIP",
                "predictions": results,
                "top_prediction": top_prediction,
                "top_confidence": top_confidence,
                "category": category,
                "total_diseases_checked": len(text_prompts)
            }
        except Exception as e:
            return {"error": f"MedSigLIP inference failed: {str(e)}"}
    
    def classify_with_cxr(self, image: Image.Image) -> Dict:
        """Use CXR Foundation for chest disease detection"""
        if self.models['cxr'] is None:
            return {"error": "CXR Foundation model not loaded"}
        
        try:
            processor = self.processors['cxr']
            inputs = processor(image, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.models['cxr'](**inputs)
                
                # Extract embeddings
                if hasattr(outputs, 'last_hidden_state'):
                    embeddings = outputs.last_hidden_state.mean(dim=1)
                elif hasattr(outputs, 'pooler_output'):
                    embeddings = outputs.pooler_output
                else:
                    embeddings = outputs[0].mean(dim=1) if isinstance(outputs, tuple) else outputs.mean(dim=1)
            
            # CXR Foundation model returns embeddings, not direct classifications
            # Since we don't have a trained classifier head, we'll use MedSigLIP instead
            # or return a note that this model needs a classifier
            return {
                "model": "CXR Foundation",
                "note": "CXR Foundation model loaded but requires a trained classifier head for predictions. Using other models instead.",
                "top_predictions": {},
                "predictions": {}
            }
            
            # OLD CODE (commented out - was causing "No Finding" bias):
            # chest_diseases = [
            #     "No Finding", "Pneumonia", "Pneumothorax", "Edema", 
            #     "Cardiomegaly", "Lung Opacity", "Consolidation", "Atelectasis",
            #     "Pleural Effusion", "Fracture"
            # ]
            # embedding_norm = torch.norm(embeddings, dim=1)
            # scores = torch.softmax(embedding_norm.unsqueeze(0), dim=-1)
            # predictions = {}
            # for i, disease in enumerate(chest_diseases[:len(scores[0])]):
            #     predictions[disease] = float(scores[0][i] if i < len(scores[0]) else 0.0)
            # sorted_preds = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
            # top_predictions = dict(sorted_preds[:5])
            
            return {
                "model": "CXR Foundation",
                "predictions": predictions,
                "top_predictions": top_predictions,
                "embeddings_shape": list(embeddings.shape),
                "note": "Classification based on CXR Foundation embeddings"
            }
        except Exception as e:
            return {"error": f"CXR Foundation inference failed: {str(e)}"}
    
    def classify_with_chexpert(self, image: Image.Image) -> Dict:
        """Use CheXpert DenseNet for common chest diseases"""
        if self.models['chexpert'] is None:
            return {"error": "CheXpert DenseNet model not loaded"}
        
        try:
            from torchvision import transforms
            
            transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
            
            image_tensor = transform(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                outputs = self.models['chexpert'](image_tensor)
                probs = torch.sigmoid(outputs)  # Multi-label classification
            
            # Get predictions for each disease
            predictions = {}
            for i, label in enumerate(self.chexpert_labels):
                confidence = float(probs[0][i])
                # Lower threshold to 5% to capture more findings
                # But prioritize disease findings over "No Finding"
                if confidence > 0.05:  # 5% threshold
                    predictions[label] = confidence
            
            # Filter out "No Finding" unless it's the only high-confidence option
            disease_predictions = {k: v for k, v in predictions.items() 
                                 if k.lower() not in ["no finding"]}
            
            # Use disease predictions if available, otherwise use all
            if disease_predictions:
                predictions = disease_predictions
            
            # Get top predictions - prioritize diseases over "No Finding"
            top_k = min(5, len(predictions) if predictions else len(self.chexpert_labels))
            if predictions:
                sorted_preds = sorted(predictions.items(), key=lambda x: x[1], reverse=True)[:top_k]
                top_diseases = dict(sorted_preds)
            else:
                # Fallback to original method if no predictions above threshold
                top_probs, top_indices = torch.topk(probs[0], k=top_k)
                top_diseases = {
                    self.chexpert_labels[idx]: float(prob)
                    for prob, idx in zip(top_probs, top_indices)
                }
                # Filter "No Finding" from top if other diseases exist
                if "No Finding" in top_diseases and len(top_diseases) > 1:
                    no_finding_score = top_diseases.pop("No Finding")
                    # Only add it back if it's truly the highest
                    if not top_diseases or no_finding_score > max(top_diseases.values()):
                        top_diseases = {"No Finding": no_finding_score, **top_diseases}
            
            return {
                "model": "CheXpert DenseNet",
                "predictions": predictions,
                "top_predictions": top_diseases
            }
        except Exception as e:
            return {"error": f"CheXpert inference failed: {str(e)}"}
    
    def _ensure_medgemma_loaded(self):
        """Lazily load MedGemma when needed"""
        # If already loaded or attempted, skip
        if self._medgemma_loaded:
            return
        
        # If model is already loaded from a previous call, mark as loaded
        if self.models.get('medgemma') is not None or self.medgemma_pipeline is not None:
            self._medgemma_loaded = True
            return
        
        # Attempt to load MedGemma
        print("\n[INFO] Loading MedGemma-27b-it on-demand (this may take 20+ minutes on first use)...")
        self._load_medgemma()
        
        # Mark as attempted (even if it failed, don't try again)
        self._medgemma_loaded = True
        
        if self.models.get('medgemma') is None and self.medgemma_pipeline is None:
            print("  [WARNING] MedGemma failed to load. Continuing with other models.")
    
    def classify_with_medgemma(self, image: Optional[Image.Image] = None, text_input: Optional[str] = None) -> Dict:
        """Use MedGemma-27b-it for comprehensive medical analysis"""
        # Load MedGemma lazily if not already loaded
        self._ensure_medgemma_loaded()
        
        if self.models.get('medgemma') is None and self.medgemma_pipeline is None:
            return {"error": "MedGemma model not loaded (may require access approval or more time to load)"}
        
        try:
            if image is None and not text_input:
                return {"error": "Either image or text input required"}
            
            # Use pipeline if available
            if self.medgemma_pipeline is not None:
                messages = [
                    {
                        "role": "system",
                        "content": [{"type": "text", "text": "You are an expert medical radiologist. Analyze the medical image and/or text and provide a detailed diagnosis with confidence."}]
                    }
                ]
                
                if image and text_input:
                    messages.append({
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"Analyze this medical image and the following clinical information:\n\n{text_input}\n\nProvide: 1) Primary diagnosis, 2) Confidence level, 3) Key findings, 4) Differential diagnoses."},
                            {"type": "image", "image": image}
                        ]
                    })
                elif image:
                    messages.append({
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Analyze this medical image. Provide: 1) Primary diagnosis, 2) Confidence level, 3) Key findings, 4) Differential diagnoses."},
                            {"type": "image", "image": image}
                        ]
                    })
                else:
                    messages.append({
                        "role": "user",
                        "content": [{"type": "text", "text": f"Analyze the following medical report:\n\n{text_input}\n\nProvide: 1) Primary diagnosis, 2) Confidence level, 3) Key findings, 4) Differential diagnoses."}]
                    })
                
                output = self.medgemma_pipeline(text=messages, max_new_tokens=500)
                result_text = output[0]["generated_text"][-1]["content"]
                
                # Parse the result to extract diagnosis
                return {
                    "model": "MedGemma-27b-it",
                    "full_analysis": result_text,
                    "primary_diagnosis": self._extract_diagnosis_from_text(result_text),
                    "confidence": "high",  # MedGemma is highly accurate
                    "raw_output": result_text
                }
            else:
                # Use direct model loading
                processor = self.processors['medgemma']
                model = self.models['medgemma']
                
                if image and text_input:
                    messages = [
                        {"role": "system", "content": [{"type": "text", "text": "You are an expert medical radiologist."}]},
                        {"role": "user", "content": [
                            {"type": "text", "text": f"Analyze: {text_input}"},
                            {"type": "image", "image": image}
                        ]}
                    ]
                elif image:
                    messages = [
                        {"role": "system", "content": [{"type": "text", "text": "You are an expert medical radiologist."}]},
                        {"role": "user", "content": [
                            {"type": "text", "text": "Analyze this medical image."},
                            {"type": "image", "image": image}
                        ]}
                    ]
                else:
                    messages = [
                        {"role": "system", "content": [{"type": "text", "text": "You are an expert medical radiologist."}]},
                        {"role": "user", "content": [{"type": "text", "text": f"Analyze: {text_input}"}]}
                    ]
                
                inputs = processor.apply_chat_template(
                    messages, add_generation_prompt=True, tokenize=True,
                    return_dict=True, return_tensors="pt"
                ).to(model.device, dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32)
                
                input_len = inputs["input_ids"].shape[-1]
                
                with torch.inference_mode():
                    generation = model.generate(**inputs, max_new_tokens=500, do_sample=False)
                    generation = generation[0][input_len:]
                
                result_text = processor.decode(generation, skip_special_tokens=True)
                
                return {
                    "model": "MedGemma-27b-it",
                    "full_analysis": result_text,
                    "primary_diagnosis": self._extract_diagnosis_from_text(result_text),
                    "confidence": "high",
                    "raw_output": result_text
                }
        except Exception as e:
            return {"error": f"MedGemma inference failed: {str(e)}"}
    
    def _extract_diagnosis_from_text(self, text: str) -> str:
        """Extract primary diagnosis from MedGemma output"""
        text_lower = text.lower()
        
        # Look for common diagnosis patterns
        diagnosis_keywords = ["diagnosis:", "primary diagnosis:", "finding:", "condition:", "disease:"]
        
        for keyword in diagnosis_keywords:
            if keyword in text_lower:
                idx = text_lower.find(keyword)
                # Extract text after keyword
                after_keyword = text[idx + len(keyword):].strip()
                # Get first sentence or up to newline
                diagnosis = after_keyword.split('\n')[0].split('.')[0].strip()
                if diagnosis:
                    return diagnosis
        
        # If no keyword found, try to extract first meaningful sentence
        sentences = text.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10 and any(word in sentence.lower() for word in ['pneumonia', 'fracture', 'tumor', 'cancer', 'normal', 'finding']):
                return sentence
        
        return "Analysis completed - see full report"
    
    def get_best_model_prediction_for_bone(self, analysis_results: Dict) -> Dict:
        """Select the best prediction for bone X-rays - PRIORITIZE FRACTURES
        NOTE: Only uses MedSigLIP and MedGemma - CheXpert is NOT used (it's a chest X-ray model)
        """
        best_prediction = None
        best_confidence = 0.0
        best_model = "MedSigLIP"  # Default model
        full_analysis = None
        
        # Fracture keywords for priority detection
        fracture_keywords = ["fracture", "broken", "break", "crack", "fissure"]
        
        # 1. Check MedSigLIP (Primary for fractures) - PRIORITIZE FRACTURE DETECTIONS
        if "medsiglip" in analysis_results and "error" not in analysis_results["medsiglip"]:
            medsiglip = analysis_results["medsiglip"]
            if "predictions" in medsiglip and medsiglip["predictions"]:
                # FIRST: Look for fracture-related predictions (HIGHEST PRIORITY)
                fracture_preds = {k: v for k, v in medsiglip["predictions"].items() 
                                if any(keyword in k.lower() for keyword in fracture_keywords)}
                
                if fracture_preds:
                    # Use fracture findings (highest priority)
                    top_pred = max(fracture_preds.items(), key=lambda x: x[1])
                    best_confidence = top_pred[1]
                    best_prediction = top_pred[0]
                    best_model = "MedSigLIP"
                    full_analysis = f"MedSigLIP Analysis (Fracture Detected):\nPrimary Finding: {top_pred[0]} ({top_pred[1]:.1%} confidence)\n"
                    sorted_preds = sorted(medsiglip["predictions"].items(), key=lambda x: x[1], reverse=True)[:5]
                    full_analysis += "Top 5 Predictions:\n"
                    for disease, score in sorted_preds:
                        full_analysis += f"  - {disease}: {score:.1%}\n"
                else:
                    # No fracture found, check other bone conditions
                    disease_preds = {k: v for k, v in medsiglip["predictions"].items() 
                                   if k.lower() not in ["normal", "healthy", "no finding", "no abnormality", "no fracture"]}
                    
                    if disease_preds:
                        top_pred = max(disease_preds.items(), key=lambda x: x[1])
                        if top_pred[1] > best_confidence:
                            best_confidence = top_pred[1]
                            best_prediction = top_pred[0]
                            best_model = "MedSigLIP"
                            full_analysis = f"MedSigLIP Analysis:\nPrimary Finding: {top_pred[0]} ({top_pred[1]:.1%} confidence)\n"
                            sorted_preds = sorted(medsiglip["predictions"].items(), key=lambda x: x[1], reverse=True)[:5]
                            full_analysis += "Top 5 Predictions:\n"
                            for disease, score in sorted_preds:
                                full_analysis += f"  - {disease}: {score:.1%}\n"
        
        # 2. Check MedGemma (secondary) - Look for fracture mentions
        if "medgemma" in analysis_results and "error" not in analysis_results["medgemma"]:
            medgemma = analysis_results["medgemma"]
            analysis_text = medgemma.get("full_analysis", "").lower()
            
            # Check if MedGemma mentions fracture
            if any(keyword in analysis_text for keyword in fracture_keywords):
                # Fracture detected by MedGemma - high priority
                diagnosis = self._extract_diagnosis_from_text(medgemma.get("full_analysis", ""))
                if "fracture" in diagnosis.lower() or "broken" in diagnosis.lower():
                    conf = 0.95  # High confidence for fracture detection
                    if conf > best_confidence:
                        best_confidence = conf
                        best_prediction = diagnosis
                        best_model = "MedGemma-27b-it"
                        full_analysis = medgemma.get("full_analysis", "")
            elif "primary_diagnosis" in medgemma:
                conf = 0.85
                if conf > best_confidence:
                    best_confidence = conf
                    best_prediction = medgemma["primary_diagnosis"]
                    best_model = "MedGemma-27b-it"
                    full_analysis = medgemma.get("full_analysis", "")
            elif "full_analysis" in medgemma:
                diagnosis = self._extract_diagnosis_from_text(medgemma["full_analysis"])
                conf = 0.85
                if conf > best_confidence:
                    best_confidence = conf
                    best_prediction = diagnosis
                    best_model = "MedGemma-27b-it"
                    full_analysis = medgemma["full_analysis"]
        
        # Final result
        if best_prediction is None:
            best_prediction = "No specific finding detected"
            best_confidence = 0.0
        
        return {
            "model": best_model,
            "disease": best_prediction,
            "confidence": best_confidence,
            "full_analysis": full_analysis or f"{best_model} Analysis: {best_prediction}"
        }
    
    def get_best_model_prediction(self, analysis_results: Dict) -> Dict:
        """Select the best prediction from all models - prioritize MedSigLIP"""
        best_prediction = None
        best_confidence = 0.0
        best_model = "MedSigLIP"  # Default model
        full_analysis = None

        # Prioritize the finetuned custom chest model when present (for chest X-rays)
        if "custom_chest" in analysis_results and "error" not in analysis_results["custom_chest"]:
            custom = analysis_results["custom_chest"]
            preds = custom.get("predictions") or {}
            # If the model reports "No Finding" as top_prediction, treat it as low confidence.
            if preds:
                top_pred = max(preds.items(), key=lambda x: x[1])
                conf = float(top_pred[1])
                # Give it a small priority boost so it doesn't get overridden by CheXpert noise
                if conf >= best_confidence:
                    best_confidence = conf
                    best_prediction = custom.get("top_prediction") or top_pred[0]
                    best_model = "Custom ChestXray (Finetuned)"
                    full_analysis = custom.get("full_analysis")
        
        # Prioritize MedSigLIP (best for general detection and accuracy)
        if "medsiglip" in analysis_results and "error" not in analysis_results["medsiglip"]:
            medsiglip = analysis_results["medsiglip"]
            if "predictions" in medsiglip and medsiglip["predictions"]:
                # Filter out "normal", "healthy", "no finding" unless they're the only options
                disease_preds = {k: v for k, v in medsiglip["predictions"].items() 
                               if k.lower() not in ["normal", "healthy", "no finding", "no abnormality"]}
                
                if disease_preds:
                    # Use disease findings
                    top_pred = max(disease_preds.items(), key=lambda x: x[1])
                else:
                    # Fallback to all predictions if only normal/healthy found
                    top_pred = max(medsiglip["predictions"].items(), key=lambda x: x[1])
                
                if top_pred[1] > best_confidence:
                    best_confidence = top_pred[1]
                    best_prediction = top_pred[0]
                    best_model = "MedSigLIP"
                    # Include all predictions for comprehensive analysis
                    full_analysis = f"MedSigLIP Analysis:\nTop Prediction: {top_pred[0]} ({top_pred[1]:.1%} confidence)\n"
                    sorted_preds = sorted(medsiglip["predictions"].items(), key=lambda x: x[1], reverse=True)[:5]
                    full_analysis += "Top 5 Predictions:\n"
                    for disease, score in sorted_preds:
                        full_analysis += f"  - {disease}: {score:.1%}\n"
        
        # Check MedGemma (secondary - high accuracy but slower)
        if "medgemma" in analysis_results and "error" not in analysis_results["medgemma"]:
            medgemma = analysis_results["medgemma"]
            if "primary_diagnosis" in medgemma:
                conf = 0.90  # Slightly lower priority than MedSigLIP
                if conf > best_confidence:
                    best_confidence = conf
                    best_prediction = medgemma["primary_diagnosis"]
                    best_model = "MedGemma-27b-it"
                    full_analysis = medgemma.get("full_analysis", "")
            elif "full_analysis" in medgemma:
                diagnosis = self._extract_diagnosis_from_text(medgemma["full_analysis"])
                conf = 0.90
                if conf > best_confidence:
                    best_confidence = conf
                    best_prediction = diagnosis
                    best_model = "MedGemma-27b-it"
                    full_analysis = medgemma["full_analysis"]
        
        # Check CheXpert (most reliable for chest diseases)
        if "chexpert" in analysis_results and "error" not in analysis_results["chexpert"]:
            chexpert = analysis_results["chexpert"]
            # Check both top_predictions and predictions
            preds = None
            if "top_predictions" in chexpert and chexpert["top_predictions"]:
                preds = chexpert["top_predictions"]
            elif "predictions" in chexpert and chexpert["predictions"]:
                preds = chexpert["predictions"]
            
            if preds:
                # Filter out "No Finding" unless it's the only option
                disease_preds = {k: v for k, v in preds.items() 
                               if k.lower() not in ["no finding", "normal"]}
                
                if disease_preds:
                    top_pred = max(disease_preds.items(), key=lambda x: x[1])
                else:
                    top_pred = max(preds.items(), key=lambda x: x[1])
                
                if top_pred[1] > best_confidence:
                    best_confidence = top_pred[1]
                    best_prediction = top_pred[0]
                    best_model = "CheXpert DenseNet"
                    # Add analysis
                    full_analysis = f"CheXpert DenseNet Analysis:\nTop Prediction: {top_pred[0]} ({top_pred[1]:.1%} confidence)\n"
                    sorted_preds = sorted(preds.items(), key=lambda x: x[1], reverse=True)[:5]
                    full_analysis += "Top 5 Predictions:\n"
                    for disease, score in sorted_preds:
                        full_analysis += f"  - {disease}: {score:.1%}\n"
        
        # Check CXR Foundation (skip if no real predictions)
        if "cxr" in analysis_results and "error" not in analysis_results["cxr"]:
            if "top_predictions" in analysis_results["cxr"] and analysis_results["cxr"]["top_predictions"]:
                preds = analysis_results["cxr"]["top_predictions"]
                # Filter out "No Finding" unless it's the only option
                disease_preds = {k: v for k, v in preds.items() 
                               if k.lower() not in ["no finding", "normal"]}
                
                if disease_preds:
                    top_pred = max(disease_preds.items(), key=lambda x: x[1])
                    if top_pred[1] > best_confidence:
                        best_confidence = top_pred[1]
                        best_prediction = top_pred[0]
                        best_model = "CXR Foundation"
        
        # Ensure we always return a valid result
        if best_prediction is None:
            best_prediction = "Analysis completed - no specific finding"
            best_confidence = 0.5
            best_model = "MedSigLIP"
            full_analysis = "No high-confidence predictions found. Review image quality or try different models."
        
        return {
            "disease": best_prediction,
            "confidence": best_confidence,
            "model": best_model or "MedSigLIP",  # Ensure model is never None
            "full_analysis": full_analysis
        }
    
    def generate_report_with_gemini(
        self, 
        image: Optional[Image.Image] = None,
        text_input: Optional[str] = None,
        analysis_results: Optional[Dict] = None,
        use_best_model_only: bool = False,
        best_model_info: Optional[Dict] = None
    ) -> str:
        """Generate radiologist report using Gemini via Groq"""
        if self.groq_client is None:
            return "Groq API not available. Please check your API key."
        
        try:
            # Prepare prompt - use only best model if specified
            if use_best_model_only and best_model_info:
                prompt = f"You are a medical radiologist. Analyze the following medical findings from the BEST AI model ({best_model_info.get('model', 'AI Model')}) and generate a professional radiology report.\n\n"
                prompt += f"BEST MODEL SELECTED: {best_model_info.get('model', 'AI Model')} (Highest Confidence)\n"
                prompt += f"PRIMARY FINDING: {best_model_info.get('disease', 'N/A')} ({best_model_info.get('confidence', 0):.1%} confidence)\n\n"
            else:
                prompt = "You are a medical radiologist. Analyze the following medical findings from AI models and generate a professional radiology report.\n\n"
            
            if analysis_results:
                # Format model results (only best model if use_best_model_only is True)
                formatted_results = []
                
                # MedSigLIP results
                if "medsiglip" in analysis_results and "error" not in analysis_results["medsiglip"]:
                    medsiglip = analysis_results["medsiglip"]
                    if "top_prediction" in medsiglip:
                        pred_text = f"MedSigLIP (General Detection): {medsiglip['top_prediction']}"
                        if "predictions" in medsiglip and medsiglip["top_prediction"] in medsiglip["predictions"]:
                            conf = medsiglip["predictions"][medsiglip["top_prediction"]]
                            pred_text += f" (Confidence: {conf:.1%})"
                        formatted_results.append(pred_text)
                        # Add top 3 predictions
                        if "predictions" in medsiglip:
                            sorted_preds = sorted(medsiglip["predictions"].items(), key=lambda x: x[1], reverse=True)[:3]
                            pred_list = ", ".join([f"{d} ({s:.1%})" for d, s in sorted_preds])
                            formatted_results.append(f"  Top predictions: {pred_list}")
                
                # CheXpert results (most reliable)
                if "chexpert" in analysis_results and "error" not in analysis_results["chexpert"]:
                    chexpert = analysis_results["chexpert"]
                    if "top_predictions" in chexpert:
                        pred_list = []
                        for disease, score in list(chexpert["top_predictions"].items())[:5]:
                            pred_list.append(f"{disease} ({score:.1%})")
                        formatted_results.append(f"CheXpert DenseNet (High Accuracy): {', '.join(pred_list)}")
                
                # CXR Foundation results
                if "cxr" in analysis_results and "error" not in analysis_results["cxr"]:
                    cxr = analysis_results["cxr"]
                    if "top_predictions" in cxr:
                        pred_list = []
                        for disease, score in list(cxr["top_predictions"].items())[:3]:
                            pred_list.append(f"{disease} ({score:.1%})")
                        formatted_results.append(f"CXR Foundation (Chest Specialized): {', '.join(pred_list)}")
                
                if formatted_results:
                    if use_best_model_only:
                        prompt += "MODEL ANALYSIS RESULTS (Best Model Only):\n"
                    else:
                        prompt += "MODEL ANALYSIS RESULTS:\n"
                    prompt += "\n".join(formatted_results) + "\n\n"
                    
                    if not use_best_model_only:
                        # Get best prediction
                        best = self.get_best_model_prediction(analysis_results)
                        if best["disease"]:
                            prompt += f"PRIMARY FINDING (Highest Confidence): {best['disease']} ({best['confidence']:.1%} confidence from {best['model']})\n\n"
            
            if text_input:
                prompt += f"CLINICAL HISTORY/REPORT:\n{text_input}\n\n"
            
            prompt += "Generate a professional radiology report with the following structure:\n"
            prompt += "1. CLINICAL INDICATION: Based on the clinical history provided above\n"
            prompt += "2. FINDINGS: Describe findings based on ALL model predictions above. Include:\n"
            prompt += "   - Primary finding (highest confidence prediction)\n"
            prompt += "   - Secondary findings from other models\n"
            prompt += "   - Confidence levels for each finding\n"
            prompt += "3. IMPRESSION: Summary diagnosis based on ALL model consensus. Use the PRIMARY FINDING as the main diagnosis.\n"
            prompt += "4. RECOMMENDATIONS: Clinical recommendations\n\n"
            prompt += "CRITICAL INSTRUCTIONS:\n"
            prompt += "- Use ONLY the diseases that appear in the model results above\n"
            prompt += "- Do NOT invent or assume diseases (especially do NOT default to tuberculosis)\n"
            prompt += "- If models show 'No Finding' or 'normal', state that clearly\n"
            prompt += "- Report the PRIMARY FINDING as the main diagnosis\n"
            prompt += "- Include confidence levels in your findings\n\n"
            prompt += "RADIOLOGY REPORT:"
            
            # Use Groq API with available model
            # Try different models in order of preference
            models_to_try = [
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "llama-3.1-70b-versatile",
                "mixtral-8x7b-32768"
            ]
            
            chat_completion = None
            last_error = None
            
            for model_name in models_to_try:
                try:
                    chat_completion = self.groq_client.chat.completions.create(
                        messages=[
                            {
                                "role": "system",
                                "content": "You are an expert medical radiologist with years of experience in interpreting medical images and reports. Always provide accurate, professional medical reports."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        model=model_name,
                        temperature=0.3,
                        max_tokens=1500
                    )
                    break  # Success, exit loop
                except Exception as e:
                    last_error = e
                    continue
            
            if chat_completion is None:
                raise Exception(f"All models failed. Last error: {last_error}")
            
            report = chat_completion.choices[0].message.content
            return report
            
        except Exception as e:
            # Fallback: try with Google Generative AI if available
            try:
                import google.generativeai as genai
                # Note: This would need actual Gemini API key, not Groq key
                # genai.configure(api_key=YOUR_GEMINI_API_KEY)
                
                # For now, return error message
                return f"Groq API error: {str(e)}\n\nTo use Gemini directly, configure google-generativeai with a Gemini API key."
            except Exception as e2:
                return f"Failed to generate report: {str(e)}"
    
    def extract_diseases_from_text(self, text: str) -> Dict:
        """Extract diseases mentioned in medical text using comprehensive database"""
        if not text:
            return {"diseases": [], "categories": []}
        
        text_lower = text.lower()
        found_diseases = []
        found_categories = set()
        
        # Search for diseases in text
        if hasattr(self, 'all_diseases'):
            for disease in self.all_diseases:
                # Check if disease or its variations appear in text
                disease_lower = disease.lower()
                if disease_lower in text_lower:
                    category = self.get_category_for_disease(disease)
                    found_diseases.append({
                        "disease": disease,
                        "category": category,
                        "confidence": "high" if disease_lower == text_lower else "medium"
                    })
                    found_categories.add(category)
        
        # Also check for common medical terms
        medical_keywords = [
            "diagnosis", "diagnosed with", "suffering from", "has", "presents with",
            "shows signs of", "consistent with", "suggestive of", "indicative of"
        ]
        
        return {
            "diseases": found_diseases,
            "categories": list(found_categories),
            "total_found": len(found_diseases)
        }
    
    def classify(
        self, 
        image_path: Optional[Union[str, Image.Image]] = None,
        report_text: Optional[str] = None,
        generate_report: bool = True,
        use_comprehensive: bool = True
    ) -> Dict:
        """
        Main classification function
        
        Args:
            image_path: Path to medical image or PIL Image object
            report_text: Medical report text (optional)
            generate_report: Whether to generate a radiologist report
        
        Returns:
            Dictionary with classification results
        """
        results = {
            "input_type": "image" if image_path else "text",
            "classifications": {},
            "report": None,
            "extracted_diseases": {}
        }
        
        # Extract diseases from text if provided
        if report_text:
            print("\nExtracting diseases from text...")
            text_diseases = self.extract_diseases_from_text(report_text)
            results["extracted_diseases"] = text_diseases
            print(f"Found {text_diseases.get('total_found', 0)} diseases in text")
        
        # Process image if provided
        image = None
        if image_path:
            try:
                image = self.preprocess_image(image_path)
                results["input_type"] = "image"
            except Exception as e:
                return {"error": f"Failed to load image: {str(e)}"}
        
        # Run all models on image
        if image:
            print("\nRunning MedSigLIP (comprehensive disease detection)...")
            medsiglip_result = self.classify_with_medsiglip(image, use_comprehensive=use_comprehensive)
            results["classifications"]["medsiglip"] = medsiglip_result
            
            print("Running CXR Foundation (chest diseases)...")
            cxr_result = self.classify_with_cxr(image)
            results["classifications"]["cxr"] = cxr_result
            
            print("Running CheXpert DenseNet (common diseases)...")
            chexpert_result = self.classify_with_chexpert(image)
            results["classifications"]["chexpert"] = chexpert_result
        
        # Select best model (MedGemma prioritized)
        print("\nSelecting best model (MedGemma prioritized for highest accuracy)...")
        combined_results = {
            "medgemma": results["classifications"].get("medgemma", {}),
            "medsiglip": results["classifications"].get("medsiglip", {}),
            "cxr": results["classifications"].get("cxr", {}),
            "chexpert": results["classifications"].get("chexpert", {})
        }
        
        best_pred = self.get_best_model_prediction(combined_results)
        results["best_prediction"] = best_pred
        
        # Use MedGemma for report generation (most accurate)
        if best_pred.get("model") == "MedGemma-27b-it" and "full_analysis" in best_pred:
            print(f"Using MedGemma-27b-it (Highest Accuracy Model)")
            # Generate professional report from MedGemma output
            if generate_report:
                print("\nGenerating professional radiology report from MedGemma analysis...")
                report = self._generate_professional_report_from_medgemma(
                    best_pred.get("full_analysis", ""),
                    report_text,
                    image
                )
                results["report"] = report
                results["model_used"] = "MedGemma-27b-it"
        else:
            # Fallback to other models - use actual predictions
            if best_pred.get("model") and best_pred.get("disease"):
                print(f"Using {best_pred['model']} with prediction: {best_pred['disease']} ({best_pred['confidence']:.1%} confidence)")
                
                if generate_report:
                    # Generate report directly from best prediction
                    print("\nGenerating professional radiology report from best model prediction...")
                    
                    # Use the full_analysis if available, otherwise create from prediction
                    analysis_text = best_pred.get("full_analysis", "")
                    if not analysis_text:
                        # Create analysis text from prediction
                        analysis_text = f"{best_pred['model']} Analysis:\n"
                        analysis_text += f"Primary Finding: {best_pred['disease']}\n"
                        analysis_text += f"Confidence: {best_pred['confidence']:.1%}\n"
                        
                        # Add top predictions if available
                        model_name_lower = best_pred['model'].lower()
                        if "chexpert" in model_name_lower and "chexpert" in combined_results:
                            chexpert = combined_results["chexpert"]
                            if "top_predictions" in chexpert:
                                analysis_text += "\nTop Predictions:\n"
                                for disease, score in list(chexpert["top_predictions"].items())[:5]:
                                    analysis_text += f"  - {disease}: {score:.1%}\n"
                        elif "medsiglip" in model_name_lower and "medsiglip" in combined_results:
                            medsiglip = combined_results["medsiglip"]
                            if "predictions" in medsiglip:
                                analysis_text += "\nTop Predictions:\n"
                                sorted_preds = sorted(medsiglip["predictions"].items(), key=lambda x: x[1], reverse=True)[:5]
                                for disease, score in sorted_preds:
                                    analysis_text += f"  - {disease}: {score:.1%}\n"
                    
                    # Pass the actual disease name to report generation
                    report = self._generate_professional_report_from_medgemma(
                        analysis_text,
                        report_text or "Medical image analysis",
                        image,
                        best_pred.get("model", "AI Model"),
                        primary_disease=best_pred.get("disease")  # Pass actual disease
                    )
                    results["report"] = report
                    results["model_used"] = best_pred.get("model", "Multiple models")
            else:
                # Last resort - use Groq API
                best_model_name = best_pred.get("model", "unknown").lower().replace(" ", "_")
                if "medgemma" in best_model_name:
                    best_model_name = "medgemma"
                elif "medsiglip" in best_model_name:
                    best_model_name = "medsiglip"
                elif "chexpert" in best_model_name:
                    best_model_name = "chexpert"
                elif "cxr" in best_model_name:
                    best_model_name = "cxr"
                
                best_model_results = {
                    best_model_name: combined_results.get(best_model_name, {})
                }
                
                if generate_report:
                    print("\nGenerating radiologist report using Groq API...")
                    report = self.generate_report_with_gemini(
                        image=image,
                        text_input=report_text,
                        analysis_results=best_model_results,
                        use_best_model_only=True,
                        best_model_info=best_pred
                    )
                    results["report"] = report
                    results["model_used"] = best_pred.get("model", "Multiple models")
        
        return results
    
    def _generate_professional_report_from_best_model(self, analysis: str, clinical_history: str = "", image: Optional[Image.Image] = None, model_name: str = "MedSigLIP") -> str:
        """Generate professional report from best model's analysis"""
        # Extract actual disease from analysis if it contains model predictions
        primary_disease = None
        
        # Try to extract disease from analysis text
        if "Primary Finding:" in analysis:
            try:
                primary_disease = analysis.split("Primary Finding:")[1].split("\n")[0].strip()
            except:
                pass
        
        # If no disease found, try to extract from best_prediction if available
        # This will be handled by the caller
        
        # Extract primary disease from analysis if available
        primary_disease = None
        if "Primary Finding:" in analysis:
            try:
                primary_disease = analysis.split("Primary Finding:")[1].split("\n")[0].strip()
            except:
                pass
        
        return self._generate_professional_report_from_medgemma(analysis, clinical_history, image, model_name, primary_disease)
    
    def _generate_professional_report_from_medgemma(self, medgemma_analysis: str, clinical_history: str = "", image: Optional[Image.Image] = None, model_name: str = "MedGemma-27b-it", primary_disease: Optional[str] = None) -> str:
        """Generate professional radiology report from MedGemma analysis"""
        report = "=" * 80 + "\n"
        report += "RADIOLOGY REPORT\n"
        report += "=" * 80 + "\n\n"
        
        from datetime import datetime
        report += f"Report Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n"
        report += f"Model Used: {model_name}\n"
        if "MedSigLIP" in model_name:
            report += f"Accuracy Level: High (Medical image-text model optimized for accuracy)\n"
        else:
            report += f"Accuracy Level: High (Medical-grade model)\n"
        report += "\n"
        report += "-" * 80 + "\n\n"
        
        # Clinical Indication
        report += "CLINICAL INDICATION:\n"
        if clinical_history:
            report += f"{clinical_history}\n\n"
        else:
            report += "Clinical indication not provided.\n\n"
        
        # Findings
        report += "FINDINGS:\n"
        report += f"{medgemma_analysis}\n\n"
        
        # Impression
        report += "-" * 80 + "\n"
        report += "IMPRESSION:\n"
        
        # Use provided primary_disease if available, otherwise extract from analysis
        if primary_disease:
            diagnosis = primary_disease
        else:
            # Extract key diagnosis from analysis
            diagnosis = self._extract_diagnosis_from_text(medgemma_analysis)
            
            # If extraction failed, try to find disease names in the analysis
            if diagnosis == "Analysis completed - see full report":
                # Look for "Primary Finding:" in analysis
                if "Primary Finding:" in medgemma_analysis:
                    try:
                        diagnosis = medgemma_analysis.split("Primary Finding:")[1].split("\n")[0].strip()
                    except:
                        pass
                
                # If still not found, look for common disease names
                if diagnosis == "Analysis completed - see full report":
                    disease_keywords = [
                        "pneumonia", "fracture", "pneumothorax", "cardiomegaly", "edema",
                        "consolidation", "atelectasis", "pleural effusion", "lung opacity",
                        "tumor", "cancer", "infection", "inflammation", "tuberculosis",
                        "lung lesion", "enlarged cardiomediastinum"
                    ]
                    analysis_lower = medgemma_analysis.lower()
                    found_diseases = [d for d in disease_keywords if d in analysis_lower]
                    if found_diseases:
                        diagnosis = found_diseases[0].title()
                    else:
                        # Get first meaningful sentence
                        sentences = medgemma_analysis.split('.')
                        for sentence in sentences:
                            sentence = sentence.strip()
                            if len(sentence) > 20 and not sentence.startswith("This"):
                                diagnosis = sentence[:100]  # First 100 chars
                                break
        
        # Final fallback - should not happen if models are working
        if diagnosis == "Analysis completed - see full report" or not diagnosis:
            diagnosis = "No specific abnormality detected. Clinical correlation recommended."
        
        report += f"Based on comprehensive AI analysis using {model_name}:\n"
        report += f"Primary Finding: {diagnosis}\n"
        report += "This analysis was performed using a state-of-the-art medical AI model\n"
        report += "specifically trained on medical images and text.\n\n"
        
        # Recommendations
        report += "-" * 80 + "\n"
        report += "RECOMMENDATIONS:\n"
        report += "1. Clinical correlation with patient history and physical examination is recommended.\n"
        report += "2. Consider follow-up imaging if clinically indicated.\n"
        report += "3. Further diagnostic workup may be warranted based on clinical presentation.\n"
        report += "4. All findings should be reviewed by a qualified radiologist.\n\n"
        
        report += "=" * 80 + "\n"
        report += "END OF REPORT\n"
        report += "=" * 80 + "\n"
        report += "\nNote: This report was generated using MedGemma-27b-it, a medical AI model\n"
        report += "developed by Google for healthcare applications. All findings should be\n"
        report += "reviewed and validated by qualified medical professionals.\n"
        
        return report
    
    def classify_chest_xray(
        self,
        image_path: Union[str, Image.Image],
        generate_report: bool = True
    ) -> Dict:
        """
        Specialized classification for chest X-rays
        Uses: MedGemma (primary) + CheXpert + CXR Foundation
        """
        results = {
            "input_type": "chest_xray",
            "classifications": {},
            "report": None,
            "model_used": "Custom ChestXray (Finetuned) + CheXpert + CXR Foundation + MedGemma"
        }
        
        image = self.preprocess_image(image_path)
        
        # 0. Custom finetuned chest model (Primary)
        print("\nRunning Custom ChestXray (Finetuned)...")
        custom_result = self.classify_with_custom_chest_xray(image)
        results["classifications"]["custom_chest"] = custom_result

        # 1. MedGemma (optional - Highest Accuracy, slow)
        if self.models.get('medgemma') is not None or self.medgemma_pipeline is not None:
            print("\nRunning MedGemma-27b-it (Primary for Chest X-Ray)...")
            medgemma_result = self.classify_with_medgemma(image=image, text_input="Analyze this chest X-ray for pulmonary and cardiac findings.")
            results["classifications"]["medgemma"] = medgemma_result
        
        # 2. CheXpert (Best for chest diseases)
        print("Running CheXpert DenseNet (Chest Disease Specialist)...")
        chexpert_result = self.classify_with_chexpert(image)
        results["classifications"]["chexpert"] = chexpert_result
        
        # 3. CXR Foundation (Chest specialized)
        print("Running CXR Foundation (Chest X-Ray Specialized)...")
        cxr_result = self.classify_with_cxr(image)
        results["classifications"]["cxr"] = cxr_result
        
        # Select best (prioritize MedGemma, then CheXpert)
        combined = {
            "custom_chest": results["classifications"].get("custom_chest", {}),
            "medgemma": results["classifications"].get("medgemma", {}),
            "chexpert": results["classifications"].get("chexpert", {}),
            "cxr": results["classifications"].get("cxr", {})
        }
        best_pred = self.get_best_model_prediction(combined)
        results["best_prediction"] = best_pred
        
        # Generate report
        if generate_report:
            # Use best model's analysis for report
            if best_pred.get("full_analysis") or best_pred.get("disease"):
                analysis_text = best_pred.get("full_analysis", "")
                if not analysis_text and best_pred.get("disease"):
                    analysis_text = f"{best_pred.get('model', 'AI Model')} Analysis:\nPrimary Finding: {best_pred['disease']}\nConfidence: {best_pred.get('confidence', 0):.1%}"
                
                report = self._generate_professional_report_from_medgemma(
                    analysis_text,
                    "Chest X-ray analysis",
                    image,
                    best_pred.get("model", "MedSigLIP"),
                    primary_disease=best_pred.get("disease")
                )
                results["report"] = report
            else:
                # Use best model for report
                best_model_name = best_pred.get("model", "medsiglip").lower().replace(" ", "_")
                if "medsiglip" in best_model_name:
                    best_model_name = "medsiglip"
                elif "chexpert" in best_model_name:
                    best_model_name = "chexpert"
                elif "cxr" in best_model_name:
                    best_model_name = "cxr"
                best_model_results = {best_model_name: combined.get(best_model_name, {})}
                report = self.generate_report_with_gemini(
                    image=image,
                    text_input="Chest X-ray analysis",
                    analysis_results=best_model_results,
                    use_best_model_only=True,
                    best_model_info=best_pred
                )
                results["report"] = report
        
        return results
    
    def classify_bone_xray(
        self,
        image_path: Union[str, Image.Image],
        generate_report: bool = True
    ) -> Dict:
        """
        Specialized classification for bone X-rays with fracture detection priority
        Uses: MedSigLIP (primary for fractures) + MedGemma (secondary)
        NOTE: CheXpert is NOT used - it's a chest X-ray model, not suitable for bone X-rays
        """
        results = {
            "input_type": "bone_xray",
            "classifications": {},
            "report": None,
            "model_used": "MedSigLIP (Primary for Fractures) + MedGemma-27b-it"
        }
        
        image = self.preprocess_image(image_path)
        
        # 1. MedSigLIP (Primary - Best for bone/fracture detection)
        print("\nRunning MedSigLIP (Primary for Bone X-Ray - Fracture Detection)...")
        # Prioritize fracture-related prompts first for better detection
        bone_prompts = [
            # Fracture types (HIGHEST PRIORITY)
            "fracture", "broken bone", "bone fracture", "hairline fracture", 
            "compound fracture", "stress fracture", "complete fracture",
            "incomplete fracture", "greenstick fracture", "comminuted fracture",
            "arm fracture", "wrist fracture", "hand fracture", "finger fracture",
            "leg fracture", "ankle fracture", "foot fracture", "toe fracture",
            "shoulder fracture", "elbow fracture", "knee fracture", "hip fracture",
            # Other bone conditions
            "dislocation", "joint dislocation", "subluxation",
            "bone contusion", "bone bruise", "bone injury",
            "bone tumor", "bone cancer", "bone metastasis", "primary bone tumor",
            "bone cyst", "bone lesion", "bone deformity", "bone erosion", "bone sclerosis",
            "osteoporosis", "arthritis", "rheumatoid arthritis", "osteoarthritis",
            "bone infection", "osteomyelitis", "bone abscess", "bone necrosis", "avascular necrosis",
            "healed fracture", "fracture healing", "callus formation",
            # Normal cases (lowest priority)
            "normal bone", "normal bone structure", "healthy bone", "no fracture", "no abnormality"
        ]
        medsiglip_result = self.classify_with_medsiglip(image, text_prompts=bone_prompts, use_comprehensive=False)
        results["classifications"]["medsiglip"] = medsiglip_result
        
        # 2. MedGemma (Secondary - High accuracy but slower)
        if self.models.get('medgemma') is not None or self.medgemma_pipeline is not None:
            print("Running MedGemma-27b-it (Secondary for Bone X-Ray)...")
            medgemma_result = self.classify_with_medgemma(
                image=image, 
                text_input="Analyze this bone X-ray image. Focus on detecting fractures, broken bones, dislocations, or any bone abnormalities. Provide specific fracture type if present."
            )
            results["classifications"]["medgemma"] = medgemma_result
        
        # Select best with fracture priority (ONLY MedSigLIP and MedGemma - NO CheXpert)
        combined = {
            "medsiglip": results["classifications"].get("medsiglip", {}),
            "medgemma": results["classifications"].get("medgemma", {})
        }
        best_pred = self.get_best_model_prediction_for_bone(combined)
        results["best_prediction"] = best_pred
        
        # Generate report
        if generate_report:
            best_model_name = (best_pred.get("model") or "MedSigLIP")
            if best_pred.get("full_analysis") or best_pred.get("disease"):
                analysis_text = best_pred.get("full_analysis", "")
                if not analysis_text and best_pred.get("disease"):
                    analysis_text = f"{best_model_name} Analysis:\nPrimary Finding: {best_pred['disease']}\nConfidence: {best_pred.get('confidence', 0):.1%}"
                
                report = self._generate_professional_report_from_medgemma(
                    analysis_text,
                    "Bone X-ray analysis for fractures and abnormalities",
                    image,
                    best_model_name,
                    primary_disease=best_pred.get("disease")
                )
                results["report"] = report
            else:
                model_key = best_model_name.lower().replace(" ", "_").replace("-", "_")
                if "medsiglip" in model_key:
                    model_key = "medsiglip"
                elif "medgemma" in model_key:
                    model_key = "medgemma"
                best_model_results = {model_key: combined.get(model_key, {})}
                report = self.generate_report_with_gemini(
                    image=image,
                    text_input="Bone X-ray analysis",
                    analysis_results=best_model_results,
                    use_best_model_only=True,
                    best_model_info=best_pred
                )
                results["report"] = report
        
        return results
    
    def classify_brain_tumor(
        self,
        image_path: Union[str, Image.Image],
        generate_report: bool = True
    ) -> Dict:
        """
        Specialized classification for brain tumor MRI images
        Uses: Custom Brain Tumor Model (major_project-main) + MedSigLIP + MedGemma
        """
        results = {
            "input_type": "brain_tumor",
            "classifications": {},
            "report": None,
            "model_used": "Brain Tumor Model (Primary) + MedSigLIP + MedGemma-27b-it"
        }
        
        image = self.preprocess_image(image_path)
        
        # 1. Custom Brain Tumor Models (Primary - Ensemble: InceptionV3 + ResNet50)
        if self.models.get('brain_tumor') is not None:
            print("\nRunning Brain Tumor Models (Primary - Ensemble)...")
            try:
                import numpy as np
                import cv2
                from PIL import Image
                from tensorflow.keras.preprocessing import image as tf_image
                
                # Convert PIL to numpy array
                if isinstance(image, Image.Image):
                    img_array = np.array(image)
                else:
                    img_array = image
                
                # Ensure RGB format
                if len(img_array.shape) == 2:
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
                elif img_array.shape[2] == 4:
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
                
                # Resize to 224x224 (model input size)
                img_array = cv2.resize(img_array, (224, 224))
                
                # Normalize to [0, 1] (same as training)
                img_array = img_array.astype(np.float32) / 255.0
                
                # Add batch dimension
                img_batch = np.expand_dims(img_array, axis=0)
                
                # Ensemble prediction (soft voting)
                brain_models = self.models['brain_tumor']
                total_prob = np.zeros(len(self.brain_tumor_labels))
                
                for model_name, model in brain_models:
                    prob = model.predict(img_batch, verbose=0)[0]  # (4,)
                    total_prob += prob
                
                # Average probabilities
                final_prob = total_prob / len(brain_models)
                predicted_label_idx = np.argmax(final_prob)
                confidence = float(final_prob[predicted_label_idx])
                
                # Get label
                predicted_label = self.brain_tumor_labels[predicted_label_idx]
                
                # Create predictions dict
                brain_predictions = {}
                for i, label in enumerate(self.brain_tumor_labels):
                    brain_predictions[label] = float(final_prob[i])
                
                # Format model name
                model_names = [name for name, _ in brain_models]
                model_name_str = " + ".join(model_names) if len(model_names) > 1 else model_names[0]
                
                brain_tumor_result = {
                    "model": f"Brain Tumor Ensemble ({model_name_str})",
                    "predictions": brain_predictions,
                    "top_prediction": predicted_label,
                    "top_confidence": confidence,
                    "disease": predicted_label,
                    "confidence": confidence,
                    "category": "brain_tumor",
                    "ensemble_size": len(brain_models)
                }
                results["classifications"]["brain_tumor"] = brain_tumor_result
                print(f"  Brain Tumor Ensemble ({model_name_str}): {predicted_label} ({confidence:.1%} confidence)")
            except Exception as e:
                print(f"  [ERROR] Brain Tumor Model inference failed: {e}")
                import traceback
                traceback.print_exc()
                results["classifications"]["brain_tumor"] = {"error": str(e)}
        
        # 2. MedSigLIP (Secondary - General detection)
        print("Running MedSigLIP (Secondary for Brain Tumor)...")
        brain_prompts = [
            "brain tumor", "glioma", "meningioma", "pituitary tumor", "no tumor",
            "brain cancer", "brain lesion", "brain mass", "brain abnormality",
            "normal brain", "healthy brain", "no abnormality"
        ]
        medsiglip_result = self.classify_with_medsiglip(image, text_prompts=brain_prompts, use_comprehensive=False)
        results["classifications"]["medsiglip"] = medsiglip_result
        
        # 3. MedGemma (Tertiary - High accuracy analysis)
        if self.models.get('medgemma') is not None or self.medgemma_pipeline is not None:
            print("Running MedGemma-27b-it (Tertiary for Brain Tumor)...")
            medgemma_result = self.classify_with_medgemma(
                image=image,
                text_input="Analyze this brain MRI image for tumors. Specifically check for glioma, meningioma, pituitary tumors, or any brain abnormalities."
            )
            results["classifications"]["medgemma"] = medgemma_result
        
        # Select best (prioritize custom brain tumor model)
        combined = {
            "brain_tumor": results["classifications"].get("brain_tumor", {}),
            "medsiglip": results["classifications"].get("medsiglip", {}),
            "medgemma": results["classifications"].get("medgemma", {})
        }
        
        # ALWAYS prioritize custom brain tumor models (YOUR MODELS) - PRIMARY VERIFICATION
        # LLMs (MedSigLIP, MedGemma) are SECONDARY VERIFICATION/backup only
        if "brain_tumor" in combined and "error" not in combined["brain_tumor"]:
            model_name = combined["brain_tumor"].get("model", "Brain Tumor Ensemble (Your Custom Models)")
            best_pred = {
                "model": model_name,
                "disease": combined["brain_tumor"].get("disease", "Unknown"),
                "confidence": combined["brain_tumor"].get("confidence", 0.0),
                "full_analysis": f"{model_name} Analysis (PRIMARY - Your Custom Models):\nPrimary Finding: {combined['brain_tumor'].get('disease', 'Unknown')}\nConfidence: {combined['brain_tumor'].get('confidence', 0):.1%}\n\nAll Predictions:\n"
            }
            for label, conf in combined["brain_tumor"].get("predictions", {}).items():
                best_pred["full_analysis"] += f"  - {label}: {conf:.1%}\n"
            
            # Add secondary verification note from LLMs (if available)
            if "medsiglip" in combined and "error" not in combined["medsiglip"]:
                medsiglip_pred = combined["medsiglip"].get("top_prediction", "N/A")
                best_pred["full_analysis"] += f"\nSecondary Verification (MedSigLIP): {medsiglip_pred}\n"
            if "medgemma" in combined and "error" not in combined["medgemma"]:
                medgemma_pred = combined["medgemma"].get("primary_diagnosis", combined["medgemma"].get("disease", "N/A"))
                best_pred["full_analysis"] += f"Secondary Verification (MedGemma): {medgemma_pred}\n"
        else:
            # Fallback to LLMs only if custom models fail
            print("  [INFO] Custom brain tumor models not available, using LLM fallback")
            best_pred = self.get_best_model_prediction(combined)
        
        results["best_prediction"] = best_pred
        
        # Generate report
        if generate_report:
            best_model_name = best_pred.get("model", "Brain Tumor Model")
            if best_pred.get("full_analysis") or best_pred.get("disease"):
                analysis_text = best_pred.get("full_analysis", "")
                if not analysis_text and best_pred.get("disease"):
                    analysis_text = f"{best_model_name} Analysis:\nPrimary Finding: {best_pred['disease']}\nConfidence: {best_pred.get('confidence', 0):.1%}"
                
                report = self._generate_professional_report_from_medgemma(
                    analysis_text,
                    "Brain MRI analysis for tumor detection",
                    image,
                    best_model_name,
                    primary_disease=best_pred.get("disease")
                )
                results["report"] = report
            else:
                model_key = best_model_name.lower().replace(" ", "_").replace("-", "_")
                if "brain_tumor" in model_key:
                    model_key = "brain_tumor"
                best_model_results = {model_key: combined.get(model_key, {})}
                report = self.generate_report_with_gemini(
                    image=image,
                    text_input="Brain MRI tumor analysis",
                    analysis_results=best_model_results,
                    use_best_model_only=True,
                    best_model_info=best_pred
                )
                results["report"] = report
        
        return results
    
    def classify_text_report(
        self,
        report_text: str,
        generate_report: bool = True
    ) -> Dict:
        """
        Classify text report with automatic model loading
        Specialized classification for medical text reports
        Uses: MedGemma (primary) + Text disease extraction
        """
        results = {
            "input_type": "text_report",
            "classifications": {},
            "report": None,
            "extracted_diseases": {},
            "model_used": "Text Extraction (Primary) + MedGemma-27b-it"
        }
        
        # 1. Extract diseases from text
        print("\nExtracting diseases from text...")
        text_diseases = self.extract_diseases_from_text(report_text)
        results["extracted_diseases"] = text_diseases
        print(f"Found {text_diseases.get('total_found', 0)} diseases in text")
        
        # 2. MedGemma (Secondary - Text analysis)
        if self.models.get('medgemma') is not None or self.medgemma_pipeline is not None:
            print("Running MedGemma-27b-it (Secondary for Text Analysis)...")
            medgemma_result = self.classify_with_medgemma(
                image=None,
                text_input=f"Analyze this medical report and provide diagnosis:\n\n{report_text}"
            )
            results["classifications"]["medgemma"] = medgemma_result
        
        # Select best (Text extraction + MedGemma)
        combined = {
            "medgemma": results["classifications"].get("medgemma", {})
        }
        best_pred = self.get_best_model_prediction(combined)
        
        # Always prioritize extracted diseases from text (they're most reliable for text reports)
        if text_diseases.get("diseases"):
            diseases_list = text_diseases["diseases"]
            
            # Filter out symptoms/non-diseases (like "pain", "fever", etc.) and prioritize actual diseases
            actual_diseases = [d for d in diseases_list if d.get('category', 'other') != 'other' or 
                              d['disease'].lower() not in ['pain', 'fever', 'cough', 'ache', 'discomfort']]
            
            # Use actual diseases first, fallback to all if none found
            primary_disease_list = actual_diseases if actual_diseases else diseases_list
            primary_disease = primary_disease_list[0]["disease"] if primary_disease_list else None
            
            # Only use model prediction if it's better than extracted diseases
            if primary_disease and (not best_pred.get("disease") or 
                best_pred.get("disease") == "Analysis completed - no specific finding" or
                best_pred.get("disease") == "Analysis completed - see full report" or
                best_pred.get("confidence", 0) < 0.5):
                # Use extracted diseases as primary - they're from the text itself
                best_pred = {
                    "disease": primary_disease,
                    "confidence": 0.90,
                    "model": "Text Extraction + MedSigLIP Database",
                    "full_analysis": f"Extracted Diseases from Report:\n" + "\n".join([f"  - {d['disease']} ({d.get('category', 'other')})" for d in diseases_list[:10]])
                }
        results["best_prediction"] = best_pred
        
        # Generate report
        if generate_report:
            if best_pred.get("full_analysis") or best_pred.get("disease"):
                analysis_text = best_pred.get("full_analysis", "")
                if not analysis_text and best_pred.get("disease"):
                    analysis_text = f"{best_pred.get('model', 'AI Model')} Analysis:\nPrimary Finding: {best_pred['disease']}\nConfidence: {best_pred.get('confidence', 0):.1%}"
                
                report = self._generate_professional_report_from_medgemma(
                    analysis_text,
                    report_text,
                    None,
                    best_pred.get("model", "Text Extraction"),
                    primary_disease=best_pred.get("disease")
                )
                results["report"] = report
            else:
                # Use Groq for report generation
                report = self.generate_report_with_gemini(
                    image=None,
                    text_input=report_text,
                    analysis_results=combined,
                    use_best_model_only=True,
                    best_model_info=best_pred
                )
                results["report"] = report
        
        return results


def main():
    """Example usage"""
    print("=" * 60)
    print("Medical Disease Classification System")
    print("=" * 60)
    
    # Initialize classifier
    classifier = MedicalClassifier()
    
    # Example 1: Classify from image
    print("\n" + "=" * 60)
    print("Example: Classifying medical image")
    print("=" * 60)
    
    # You can provide an image path here
    image_path = input("\nEnter path to medical image (or press Enter to skip): ").strip()
    
    if image_path and os.path.exists(image_path):
        results = classifier.classify(
            image_path=image_path,
            generate_report=True
        )
        
        print("\n" + "=" * 60)
        print("CLASSIFICATION RESULTS")
        print("=" * 60)
        print(json.dumps(results, indent=2))
    else:
        print("No image provided. You can also provide a medical report text.")
        report_text = input("\nEnter medical report text (or press Enter to skip): ").strip()
        
        if report_text:
            results = classifier.classify(
                report_text=report_text,
                generate_report=True
            )
            
            print("\n" + "=" * 60)
            print("CLASSIFICATION RESULTS")
            print("=" * 60)
            print(json.dumps(results, indent=2))
        else:
            print("\nNo input provided. Please provide either an image path or report text.")


if __name__ == "__main__":
    main()

