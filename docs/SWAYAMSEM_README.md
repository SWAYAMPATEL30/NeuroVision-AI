# SWAYAMSEM - Medical AI Classification System
## Comprehensive Project Documentation & Architecture

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Model Integration](#model-integration)
5. [Features & Capabilities](#features--capabilities)
6. [Installation & Setup](#installation--setup)
7. [Usage Guide](#usage-guide)
8. [API Reference](#api-reference)
9. [File Structure](#file-structure)
10. [Development Roadmap](#development-roadmap)
11. [Contributing](#contributing)
12. [License & Credits](#license--credits)

---

## 🎯 Project Overview

**SWAYAMSEM** (Self-Validating AI for Medical Semantics) is an advanced medical AI classification system that integrates multiple state-of-the-art models for comprehensive medical image and report analysis. The system provides specialized analysis for different medical imaging types (Chest X-rays, Bone X-rays, CT scans, MRI, etc.) and medical text reports (blood tests, pathology reports, etc.).

### Key Objectives

- **100% Accurate Disease Prediction**: Leverages multiple specialized models for maximum accuracy
- **Multi-Modal Analysis**: Supports both medical images and text reports
- **Specialized Workflows**: Optimized pipelines for different medical imaging types
- **Professional Report Generation**: Automated generation of radiology-grade reports
- **Model Caching**: Efficient model management with one-time download and reuse

---

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Chest X-Ray  │  │  Bone X-Ray  │  │ Text Reports │      │
│  │    Tab       │  │     Tab      │  │     Tab     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Medical Classifier Core Engine                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Model Selection & Orchestration Layer         │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                 │
│        ┌───────────────────┼───────────────────┐            │
│        ▼                   ▼                   ▼            │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐           │
│  │MedSigLIP │      │ MedGemma │      │ CheXpert │           │
│  │(Primary) │      │(Primary) │      │(Special) │           │
│  └──────────┘      └──────────┘      └──────────┘           │
│        │                   │                   │            │
│        └───────────────────┼───────────────────┘            │
│                            ▼                                 │
│              ┌─────────────────────────┐                     │
│              │  Best Model Selection   │                     │
│              │  & Result Aggregation   │                     │
│              └─────────────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Report Generation Layer                         │
│  ┌──────────────┐              ┌──────────────┐            │
│  │  PDF Report  │              │  Text Report │            │
│  │  Generator   │              │  Generator   │            │
│  └──────────────┘              └──────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

### Model Integration Flow

```
Input (Image/Text)
    │
    ├─→ [Preprocessing] → Image normalization, resizing
    │
    ├─→ [Model Selection] → Based on input type
    │
    ├─→ [Parallel Inference]
    │   ├─→ MedSigLIP (General medical image-text)
    │   ├─→ MedGemma-27b-it (Comprehensive analysis)
    │   ├─→ CheXpert DenseNet (Chest diseases)
    │   └─→ CXR Foundation (Chest X-ray specialized)
    │
    ├─→ [Result Aggregation] → Best model selection
    │
    ├─→ [Disease Extraction] → From predictions
    │
    ├─→ [Report Generation] → Professional radiology report
    │
    └─→ [Output] → Classification + Report (PDF/Text)
```

### Data Flow

1. **Input Processing**
   - Image: PIL Image → Preprocessing → Tensor
   - Text: String → Tokenization → Embeddings

2. **Model Inference**
   - Parallel execution of multiple models
   - Confidence scoring and ranking

3. **Post-Processing**
   - Disease name normalization
   - Category assignment
   - Confidence calibration

4. **Report Generation**
   - Structured report template
   - Findings extraction
   - Impression generation
   - Recommendations

### Bone X-Ray Pipeline Architecture

Bone X-ray analysis uses a **dedicated pipeline** separate from chest and brain workflows. **CheXpert** and **CXR Foundation** are **not** used for bone X-rays (they are chest-specific).

```
Bone X-Ray Input (Image)
         │
         ▼
┌─────────────────────────┐
│     Preprocessing       │
│  Resize, normalize      │
└───────────┬─────────────┘
            │
            ├──────────────────────────────────────────┐
            ▼                                          ▼
┌─────────────────────────────┐          ┌─────────────────────────────┐
│  MedSigLIP (Primary)        │          │  MedGemma-27b-it (Secondary) │
│  • Bone-specific prompts    │          │  • Free-form bone analysis   │
│  • Fracture-first:          │          │  • "Analyze for fractures,   │
│    fracture, broken bone,   │          │    dislocations, abnorm."    │
│    dislocation, arthritis,  │          │  • High accuracy, slower     │
│    osteoporosis, etc.       │          │  • Loaded on-demand          │
│  • Zero-shot classification │          │                              │
└─────────────┬───────────────┘          └─────────────┬───────────────┘
              │                                        │
              └────────────────┬───────────────────────┘
                               ▼
              ┌─────────────────────────────────────────┐
              │  get_best_model_prediction_for_bone()   │
              │  • Fracture-priority selection          │
              │  • Prefer fracture-related findings     │
              │  • Combine MedSigLIP + MedGemma only    │
              │  • NO CheXpert, NO CXR                  │
              └────────────────┬────────────────────────┘
                               ▼
              ┌─────────────────────────────────────────┐
              │  Report Generation                      │
              │  • Radiology-style report               │
              │  • Or Groq/Gemini backup if needed      │
              └─────────────────────────────────────────┘
                               │
                               ▼
                      Output: best_prediction, report
```

**Key points:**
- **Models used:** MedSigLIP (primary), MedGemma (secondary). **CheXpert and CXR are excluded** for bone X-rays.
- **MedSigLIP** uses a curated list of bone/fracture prompts (e.g. fracture types, dislocation, osteoporosis) for zero-shot detection.
- **Best-model selection** is fracture-aware: fracture-related predictions are prioritized over generic findings.
- **Report** is generated from the best model’s analysis or via Groq API fallback.

---

## 🛠️ Technology Stack

### Core Technologies

- **Python 3.10+**: Primary programming language
- **PyTorch**: Deep learning framework
- **Transformers (Hugging Face)**: Model loading and inference
- **Streamlit**: Web UI framework
- **PIL/Pillow**: Image processing
- **ReportLab**: PDF generation

### AI/ML Models

1. **MedSigLIP** (`fokan/MedSigLIP`)
   - Type: Vision-Language Model
   - Purpose: General medical image-text understanding
   - Best for: Zero-shot classification, semantic retrieval
   - Source: [Google Health AI Developer Foundations](https://developers.google.com/health-ai-developer-foundations/)

2. **MedGemma-27b-it** (`google/medgemma-27b-it`)
   - Type: Large Language Model (29B parameters)
   - Purpose: Comprehensive medical analysis
   - Best for: Medical image interpretation, clinical reasoning
   - Source: [Google Health AI Developer Foundations](https://developers.google.com/health-ai-developer-foundations/)

3. **CheXpert DenseNet** (DenseNet121-based)
   - Type: Convolutional Neural Network
   - Purpose: Chest X-ray disease classification
   - Best for: 14 common chest diseases
   - Source: Stanford ML Group

4. **CXR Foundation** (`google/cxr-foundation`)
   - Type: Vision Transformer
   - Purpose: Chest X-ray specialized analysis
   - Best for: Chest-specific embeddings
   - Source: [Google Health AI Developer Foundations](https://developers.google.com/health-ai-developer-foundations/)

5. **Brain Tumor Model** (InceptionV3-based) - **Custom Integration**
   - Type: Convolutional Neural Network (Transfer Learning)
   - Purpose: Brain tumor detection from MRI images
   - Best for: Glioma, Meningioma, Pituitary tumor detection
   - Accuracy: 87.7% on test set
   - Source: **major_project-main** (Custom trained model)
   - Classes: Glioma, Meningioma, Pituitary, No Tumor

### External APIs

- **Groq API**: Report generation backup (Gemini models)
- **Hugging Face Hub**: Model repository and authentication

### Dependencies

See `requirements.txt` for complete list:
- torch, torchvision, torchaudio
- transformers, huggingface-hub
- streamlit, reportlab
- pillow, numpy, pandas
- groq (for API backup)

---

## 🤖 Model Integration

### Model Loading Strategy

Models are loaded with **persistent caching** to avoid re-downloading:

```python
# Models cached in: ~/.cache/huggingface/hub/
# First run: Downloads models
# Subsequent runs: Loads from cache (fast)
```

### Model Priority & Selection

#### For Chest X-Rays:
1. **MedGemma-27b-it** (Primary) - Comprehensive analysis
2. **CheXpert DenseNet** (Secondary) - Chest disease specialist
3. **CXR Foundation** (Tertiary) - Chest-specific embeddings
4. **MedSigLIP** (Fallback) - General detection

#### For Bone X-Rays:
1. **MedSigLIP** (Primary) - Best for fracture detection; bone-specific prompts (fracture, dislocation, arthritis, etc.)
2. **MedGemma-27b-it** (Secondary) - High accuracy analysis; free-form bone/fracture interpretation  
3. **CheXpert & CXR** are **not** used for bone X-rays (chest-specific models only). Selection uses `get_best_model_prediction_for_bone` with fracture-priority logic.

#### For Brain Tumor MRI:
1. **Brain Tumor Model** (Primary) - InceptionV3-based, 87.7% accuracy
2. **MedSigLIP** (Secondary) - General brain abnormality detection
3. **MedGemma-27b-it** (Tertiary) - Comprehensive brain analysis

#### For Text Reports:
1. **Text Extraction** (Primary) - Direct disease extraction
2. **MedGemma-27b-it** (Secondary) - Clinical reasoning

### Model Caching Implementation

```python
# All models use cache_dir parameter
cache_dir = os.path.expanduser("~/.cache/huggingface/hub")

model = AutoModel.from_pretrained(
    model_name,
    cache_dir=cache_dir,  # Persistent cache
    local_files_only=False  # Check cache first, download if needed
)
```

---

## ✨ Features & Capabilities

### 1. Specialized Medical Image Analysis

- **Chest X-Ray Analysis**
  - Pneumonia, pneumothorax, cardiomegaly detection
  - Lung opacity, consolidation, atelectasis
  - Pleural effusion, edema detection

- **Bone X-Ray Analysis**
  - Fracture detection (hairline, compound, stress)
  - Dislocation and subluxation detection
  - Bone abnormalities (tumors, infections, arthritis)
  - Osteoporosis and bone density analysis

- **Brain Tumor MRI Analysis** - **NEW!**
  - Glioma detection and classification
  - Meningioma detection
  - Pituitary tumor detection
  - No tumor classification
  - Integrated from major_project-main (custom model)

### 2. Medical Text Report Analysis

- **Blood Test Reports**: Disease extraction from lab results
- **CT Scan Reports**: Pathology and imaging findings
- **Pathology Reports**: Cancer and disease diagnosis
- **Clinical Notes**: Symptom and diagnosis extraction

### 3. Professional Report Generation

- **Structured Reports**: Radiology-grade format
- **PDF Export**: Professional PDF reports
- **Text Export**: Plain text reports
- **Findings Section**: Detailed analysis
- **Impression Section**: Primary diagnosis
- **Recommendations**: Clinical follow-up suggestions

### 4. Disease Database

- **200+ Diseases**: Comprehensive disease categories
- **16 Categories**: Organized by medical specialty
- **Disease Mapping**: Automatic category assignment

### 5. Model Management

- **Automatic Caching**: Models downloaded once, reused
- **Fallback Mechanisms**: Graceful degradation if models fail
- **Error Handling**: Robust error recovery

### 6. Fine-Tuning Infrastructure

- **LLM Fine-Tuning**: Support for fine-tuning MedGemma and other LLMs
- **Custom Datasets**: JSON and Kaggle dataset support
- **Training Pipeline**: Automated training with Hugging Face Transformers
- **Model Export**: Save fine-tuned models for deployment

---

## 📦 Installation & Setup

### Prerequisites

- Python 3.10 or higher
- 8GB+ RAM (16GB recommended)
- 10GB+ free disk space (for model cache)
- CUDA-capable GPU (optional, for faster inference)

### Step 1: Clone/Download Project

```bash
cd C:\Users\ipate\Downloads\try
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Authentication

1. **Hugging Face Token**: 
   - Get token from https://huggingface.co/settings/tokens
   - Update `HF_TOKEN` in `medical_classifier.py` (line 46)
   - Accept terms for gated models:
     - https://huggingface.co/google/medgemma-27b-it
     - https://huggingface.co/google/cxr-foundation

2. **Groq API Key** (Optional, for report backup):
   - Get key from https://console.groq.com/
   - Update `GROQ_API_KEY` in `medical_classifier.py` (line 47)

### Step 4: Run Application

```bash
streamlit run app_specialized.py --server.port 8502
```

Access at: http://localhost:8502

---

## 📖 Usage Guide

### Web UI Usage

1. **Chest X-Ray Tab**
   - Upload chest X-ray image
   - Click "Analyze Chest X-Ray"
   - View results and download report

2. **Bone X-Ray Tab**
   - Upload bone X-ray image
   - Click "Analyze Bone X-Ray"
   - View fracture detection results

3. **Medical Reports Tab**
   - Paste or upload medical text report
   - Click "Analyze Report"
   - View extracted diseases

4. **General Analysis Tab**
   - Upload any medical image
   - Get general classification

### Programmatic Usage

```python
from medical_classifier import MedicalClassifier

# Initialize classifier (loads all models)
classifier = MedicalClassifier()

# Analyze chest X-ray
results = classifier.classify_chest_xray(
    image_path="chest_xray.jpg",
    generate_report=True
)

# Analyze bone X-ray
results = classifier.classify_bone_xray(
    image_path="bone_xray.jpg",
    generate_report=True
)

# Analyze text report
results = classifier.classify_text_report(
    report_text="Patient shows signs of pneumonia...",
    generate_report=True
)

# Access results
print(results["best_prediction"]["disease"])
print(results["report"])
```

---

## 📚 API Reference

### MedicalClassifier Class

#### `__init__()`
Initializes the classifier and loads all models.

#### `classify_chest_xray(image_path, generate_report=True)`
Specialized classification for chest X-rays.

**Parameters:**
- `image_path`: Path to image or PIL Image object
- `generate_report`: Whether to generate report (default: True)

**Returns:** Dictionary with:
- `classifications`: Model predictions
- `best_prediction`: Best model result
- `report`: Generated report (if requested)

#### `classify_bone_xray(image_path, generate_report=True)`
Specialized classification for bone X-rays with fracture detection.

**Parameters:** Same as `classify_chest_xray`

**Returns:** Same structure as `classify_chest_xray`

#### `classify_text_report(report_text, generate_report=True)`
Analyzes medical text reports and extracts diseases.

**Parameters:**
- `report_text`: Medical report text
- `generate_report`: Whether to generate report

**Returns:** Dictionary with:
- `extracted_diseases`: List of found diseases
- `classifications`: Model predictions
- `report`: Generated report

#### `classify_general_analysis(image_path, generate_report=True)`
General-purpose medical image classification.

---

## 📁 File Structure

```
try/
├── medical_classifier.py      # Core classification engine
├── app_specialized.py         # Streamlit UI (specialized tabs)
├── app.py                     # Original Streamlit UI
├── report_generator.py        # PDF report generation
├── disease_categories.py     # Disease database (200+ diseases)
├── fine_tune_llm.py          # LLM fine-tuning infrastructure
├── requirements.txt           # Python dependencies
├── SWAYAMSEM_README.md        # This file (comprehensive docs)
├── README.md                  # Quick start guide
├── create_backup.py           # Backup script
├── major_project-main/        # Custom model integration
│   ├── models/                # Custom trained models
│   │   ├── brainTumor.h5      # Brain tumor model (InceptionV3)
│   │   └── chest_xray.h5      # Chest X-ray model
│   └── brainTumor.ipynb      # Training notebook
│
├── Documentation/
│   ├── MODEL_STATUS.md        # Model status report
│   ├── MEDGEMMA_INTEGRATION.md
│   ├── SPECIALIZED_UI_README.md
│   └── IMPROVEMENTS_SUMMARY.md
│
└── Tests/
    ├── test_models.py         # Model testing
    ├── verify_models.py       # Model verification
    └── pipeline_check.py      # End-to-end pipeline test
```

---

## 🚀 Development Roadmap

### Completed ✅

- [x] Multi-model integration (MedSigLIP, MedGemma, CheXpert, CXR)
- [x] Specialized workflows (Chest, Bone, Brain Tumor, Text)
- [x] Professional report generation (PDF + Text)
- [x] Disease database (200+ diseases)
- [x] Model caching and persistence
- [x] Error handling and fallbacks
- [x] Streamlit UI with specialized tabs
- [x] Brain tumor detection integration (major_project-main)
- [x] Fine-tuning infrastructure for LLMs
- [x] Medical report upload support (PDF, DOCX, TXT)

### In Progress 🔄

- [ ] CI/CD integration for fine-tuning
- [ ] Additional custom model integrations

### Planned 📋

- [ ] CT Scan analysis support
- [ ] MRI analysis support
- [ ] Real-time inference optimization
- [ ] Multi-GPU support
- [ ] Docker containerization
- [ ] REST API endpoint
- [ ] Database integration for patient records
- [ ] Fine-tuning on Kaggle medical datasets

---

## 🔧 Fine-Tuning Pipeline

### Fine-Tuning Strategy

1. **Data Collection**
   - Kaggle medical imaging datasets
   - Public medical image repositories
   - Synthetic data generation
   - Custom medical text datasets

2. **Preprocessing**
   - Image normalization
   - Data augmentation
   - Label encoding
   - Text tokenization

3. **Training**
   - Transfer learning from pre-trained models
   - Domain-specific fine-tuning
   - Validation and testing
   - LLM fine-tuning with Hugging Face Transformers

4. **Deployment**
   - Model versioning
   - A/B testing
   - Performance monitoring

### Fine-Tuning Usage

```bash
# Create sample dataset
python fine_tune_llm.py --create_sample

# Fine-tune on custom dataset
python fine_tune_llm.py \
    --model google/medgemma-27b-it \
    --dataset sample_medical_data.json \
    --output ./fine_tuned_model \
    --epochs 3 \
    --batch_size 4 \
    --lr 2e-5 \
    --hf_token YOUR_HF_TOKEN

# Fine-tune on Kaggle dataset
python fine_tune_llm.py \
    --model google/medgemma-27b-it \
    --dataset kaggle/dataset-name \
    --output ./fine_tuned_model
```

### CI/CD Pipeline (Planned)

```yaml
# .github/workflows/finetune.yml
- Trigger: New training data
- Steps:
  1. Data validation
  2. Model fine-tuning
  3. Evaluation
  4. Model deployment
  5. Integration testing
```

---

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

### Code Style

- Follow PEP 8
- Use type hints
- Document all functions
- Write unit tests

---

## 📄 License & Credits

### Models & Sources

- **MedSigLIP**: [Google Health AI Developer Foundations](https://developers.google.com/health-ai-developer-foundations/)
- **MedGemma**: [Google Health AI Developer Foundations](https://developers.google.com/health-ai-developer-foundations/)
- **CXR Foundation**: [Google Health AI Developer Foundations](https://developers.google.com/health-ai-developer-foundations/)
- **CheXpert**: Stanford ML Group
- **Transformers**: Hugging Face

### Acknowledgments

- Google Health AI team for open-source medical models
- Hugging Face for model hosting and transformers library
- Stanford ML Group for CheXpert dataset and models
- Streamlit team for the excellent UI framework

### Disclaimer

This system is for **research and educational purposes only**. All medical diagnoses should be verified by qualified healthcare professionals. The system does not replace professional medical advice, diagnosis, or treatment.

---

## 📞 Support & Contact

For issues, questions, or contributions:
- Check existing documentation
- Review error logs
- Submit issues with detailed information

---

**Last Updated**: January 2025  
**Version**: 1.0.0  
**Status**: Active Development

---

*This documentation is part of the SWAYAMSEM project blackbook.*

