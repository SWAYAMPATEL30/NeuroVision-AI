# SWAYAMSEM: A Multi-Modal Medical AI Classification System with Specialized Pipelines, REST API, and Report Generation

**Research Paper — System Description, Implementation, and Features**

---

## Abstract

We present **SWAYAMSEM** (Self-Validating AI for Medical Semantics), an integrated medical AI classification system that combines multiple state-of-the-art vision and language models for medical image and text report analysis. The system supports four specialized workflows: chest X-ray, bone X-ray (fracture-focused), brain tumor MRI, and medical text report analysis. It orchestrates MedSigLIP, MedGemma-27b-it, CheXpert DenseNet, CXR Foundation, and custom brain-tumor models via modality-specific pipelines, with automatic best-model selection, radiology-style report generation (PDF and text), and a REST API for web and external integration. We describe the architecture, implementation, codebase, and all currently working features, including the FastAPI backend, Streamlit specialized UI, disease database (200+ diseases, 16 categories), fine-tuning infrastructure, and V0-ready frontend specification.

**Keywords:** Medical AI, multi-modal classification, chest X-ray, bone X-ray, brain tumor, MedSigLIP, MedGemma, CheXpert, REST API, radiology report generation, SWAYAMSEM.

---

## 1. Introduction

Automated medical image and report analysis can support triage, education, and clinical workflows when used appropriately. Recent vision–language and chest-specific models (e.g., MedSigLIP, MedGemma, CheXpert, CXR Foundation) offer complementary strengths: general medical understanding, detailed chest findings, and fracture or bone-abnormality detection. Combining them in a single, modality-aware system—with clear pipelines for chest, bone, brain, and text—remains nontrivial due to differing inputs, outputs, and failure modes.

**SWAYAMSEM** addresses this by (1) defining **modality-specific pipelines** that route inputs to the most suitable models, (2) implementing **best-model selection** per modality (e.g., fracture-priority for bone X-rays), (3) generating **radiology-style reports** (PDF and text), and (4) exposing a **REST API** and providing a **V0-ready frontend specification** for integration with modern web applications. The system also includes a **comprehensive disease database**, **fine-tuning infrastructure** for LLMs, and **fallback mechanisms** when models are unavailable.

This document serves as a **research-style system description**: we outline what is implemented, what works, the main code components, and all new features, to support reproducibility and extension.

---

## 2. Related Work and Background

### 2.1 Models Integrated

| Model | Type | Purpose | Use in SWAYAMSEM |
|-------|------|---------|------------------|
| **MedSigLIP** (`fokan/MedSigLIP`) | Vision–language | General medical image–text | General + bone (primary); brain (secondary) |
| **MedGemma-27b-it** (`google/medgemma-27b-it`) | LLM (~29B) | Medical image/report analysis | All modalities (primary or secondary); reports |
| **CheXpert DenseNet** (DenseNet121) | CNN | 14 chest diseases | Chest only |
| **CXR Foundation** (`google/cxr-foundation`) | Vision Transformer | Chest X-ray embeddings | Chest only |
| **Brain Tumor Model** (InceptionV3/ResNet50) | CNN (custom) | Glioma, meningioma, pituitary, no tumor | Brain MRI only |

**Important:** For **bone X-rays**, only MedSigLIP and MedGemma are used. **CheXpert and CXR are excluded** as they are chest-specific.

### 2.2 External Services

- **Hugging Face Hub:** Model hosting and authentication (HF token).
- **Groq API:** Optional backup for radiology report generation (Gemini) when MedGemma-based reporting is unavailable.

---

## 3. System Architecture and Methodology

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Interface Layer                         │
│  Streamlit (app_specialized.py) │ REST Clients (V0 / Next.js)   │
│  Tabs: Chest │ Bone │ Brain │ Reports │ General                  │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                   API Layer (optional)                           │
│  FastAPI (api.py): /api/classify, /classify/chest|brain|bone|text│
│  CORS enabled for localhost:3000, *.vercel.app                   │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│              MedicalClassifier (medical_classifier.py)           │
│  Model orchestration, modality routing, best-model selection,    │
│  report generation, disease extraction                           │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          ▼                       ▼                       ▼
   MedSigLIP / MedGemma    CheXpert / CXR           Brain Tumor
   (general, bone, etc.)   (chest only)             (custom)
          │                       │                       │
          └───────────────────────┼───────────────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  Report Generation (report_generator.py) │ Disease DB            │
│  PDF + text reports │ disease_categories.py (200+ diseases)      │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Modality-Specific Pipelines

1. **Chest X-Ray**  
   MedGemma (primary) → CheXpert → CXR Foundation. Best-model selection over these three. Report from best model or Groq fallback.

2. **Bone X-Ray**  
   MedSigLIP (primary, bone-specific prompts) → MedGemma (secondary). **No CheXpert, no CXR.** `get_best_model_prediction_for_bone()` applies **fracture-priority** logic (fracture-related findings preferred). Report from best model or Groq.

3. **Brain Tumor MRI**  
   Custom brain-tumor ensemble (InceptionV3 + ResNet50) primary → MedSigLIP → MedGemma. Classes: glioma, meningioma, pituitary, no tumor. Report from best model or Groq.

4. **Text Report Only**  
   Disease extraction from `disease_categories` + optional MedGemma. `classify_text_report()` returns extracted diseases and categories.

5. **General (Any Image)**  
   MedSigLIP + CheXpert + CXR (+ optional MedGemma). Best-model selection across all. Optional `report_text` for combined image+text.

### 3.3 Bone X-Ray Pipeline (Detailed)

Bone X-rays use a **dedicated pipeline**:

```
Bone X-Ray Input → Preprocessing → MedSigLIP (bone prompts) │ MedGemma (bone analysis)
                                        │                            │
                                        └──────────┬─────────────────┘
                                                   ▼
                              get_best_model_prediction_for_bone()
                              (fracture-priority; MedSigLIP + MedGemma only)
                                                   ▼
                              Report Generation → Output (best_prediction, report)
```

Bone-specific MedSigLIP prompts include fracture types, dislocations, arthritis, osteoporosis, etc. MedGemma receives a dedicated bone/fracture analysis prompt.

---

## 4. Implementation

### 4.1 Codebase Overview

| Component | File(s) | Role |
|-----------|---------|------|
| **Core engine** | `medical_classifier.py` | `MedicalClassifier` class; model loading; `classify`, `classify_chest_xray`, `classify_bone_xray`, `classify_brain_tumor`, `classify_text_report`; best-model selection; report orchestration |
| **REST API** | `api.py` | FastAPI app; `/api/classify`, `/api/classify/chest|brain|bone`, `/api/classify/text`; lazy-loaded classifier; CORS |
| **Streamlit UI** | `app_specialized.py`, `app.py` | Tabbed UI (Chest, Bone, Brain, Reports, General); upload, analyze, results, PDF/text download |
| **Report generation** | `report_generator.py` | `generate_pdf_report()` — radiology-style PDF from classification results |
| **Disease database** | `disease_categories.py` | `COMPREHENSIVE_DISEASES`, `ALL_DISEASES`, `get_category_for_disease()` — 200+ diseases, 16 categories |
| **Fine-tuning** | `fine_tune_llm.py` | MedGemma (and other LLMs) fine-tuning on JSON/Kaggle datasets; training pipeline and export |

### 4.2 MedicalClassifier — Main Entry Points

- **`classify(image_path, report_text, generate_report)`**  
  General image and/or text. Runs MedSigLIP, CheXpert, CXR; optional MedGemma. Returns `classifications`, `best_prediction`, `report`, `extracted_diseases`.

- **`classify_chest_xray(image_path, generate_report)`**  
  Chest-only pipeline. Returns same structure.

- **`classify_bone_xray(image_path, generate_report)`**  
  Bone-only pipeline (MedSigLIP + MedGemma, fracture-priority). Returns same structure.

- **`classify_brain_tumor(image_path, generate_report)`**  
  Brain MRI pipeline (custom ensemble + MedSigLIP + MedGemma). Returns same structure.

- **`classify_text_report(report_text, generate_report)`**  
  Text-only. Disease extraction + optional MedGemma. Returns `extracted_diseases`, `classifications`, `report`.

### 4.3 REST API (api.py)

- **`POST /api/classify`**  
  `multipart/form-data`: `image` (optional), `report_text` (optional), `generate_report` (default True). Uses `classify()`.

- **`POST /api/classify/chest`**  
  `image` (required), `generate_report`. Uses `classify_chest_xray()`.

- **`POST /api/classify/brain`**  
  `image` (required), `generate_report`. Uses `classify_brain_tumor()`.

- **`POST /api/classify/bone`**  
  `image` (required), `generate_report`. Uses `classify_bone_xray()`.

- **`POST /api/classify/text`**  
  `application/json`: `{ "report_text": "..." }`. Uses `classify_text_report()`.

- **`GET /api/health`**  
  Health check.

Classifier is **lazy-loaded** on first request. CORS allows `localhost:3000` and `*.vercel.app`.

### 4.4 Streamlit UI (app_specialized.py)

- **Tab 1 — Chest X-Ray:** Upload chest X-ray → Analyze → Results + PDF/text download.
- **Tab 2 — Bone X-Ray:** Upload bone X-ray → Analyze → Fracture/bone results + report.
- **Tab 3 — Medical Reports:** Paste/upload text → Analyze → Extracted diseases + report.
- **Tab 4 — General Analysis:** Any image (+ optional text) → General classification + report.
- **Tab 5 — Brain Tumor:** Upload brain MRI → Tumor type probabilities + report.

Reports are generated via `report_generator.generate_pdf_report()` and the classifier’s `report` field.

### 4.5 Dependencies

- **Core:** `torch`, `transformers`, `huggingface-hub`, `PIL`, `numpy`, `streamlit`, `reportlab`, `groq`.
- **API:** `fastapi`, `uvicorn`, `python-multipart` (`requirements_api.txt`).
- **Custom models:** `tensorflow`, `opencv-python` (brain tumor, chest custom).
- **Fine-tuning:** `datasets`, `accelerate` (see `fine_tune_llm.py`).

---

## 5. Features and Capabilities

### 5.1 Implemented Features

| Feature | Description | Status |
|---------|-------------|--------|
| **Chest X-ray analysis** | Pneumonia, pneumothorax, cardiomegaly, opacity, effusion, etc. | Working |
| **Bone X-ray analysis** | Fractures, dislocations, arthritis, osteoporosis; fracture-priority selection | Working |
| **Brain tumor MRI** | Glioma, meningioma, pituitary, no tumor; custom ensemble | Working |
| **Text report analysis** | Disease extraction from reports; 200+ diseases, 16 categories | Working |
| **General image analysis** | Any medical image; combined image+text | Working |
| **Radiology-style reports** | PDF + text; findings, impression, recommendations | Working |
| **REST API** | FastAPI endpoints for all modalities; CORS | Working |
| **Streamlit specialized UI** | Tabbed interface; upload, analyze, download | Working |
| **Disease database** | `disease_categories`; mapping to categories | Working |
| **Model caching** | Hugging Face cache; reuse across runs | Working |
| **Fallbacks** | Groq-based report generation when MedGemma unavailable | Working |
| **Fine-tuning pipeline** | `fine_tune_llm.py` for MedGemma/LLMs on custom data | Implemented |
| **V0 frontend spec** | Prompt + API contract for Next.js/V0 app | Documented |

### 5.2 New and Recent Additions

- **Bone X-ray–specific pipeline:** MedSigLIP + MedGemma only; `get_best_model_prediction_for_bone`; no CheXpert/CXR.
- **FastAPI backend (`api.py`):** REST endpoints for classify, chest, brain, bone, text; lazy classifier; CORS.
- **V0 prompt and API contract (`V0_PROMPT.md`):** Spec for Next.js 14 + Tailwind frontend; `NEXT_PUBLIC_API_URL`; modality-specific `POST` endpoints.
- **Brain tumor integration:** Custom ensemble (InceptionV3 + ResNet50) from `major_project-main`; dedicated tab and `classify_brain_tumor`.
- **Fine-tuning infrastructure:** `fine_tune_llm.py`; JSON/Kaggle datasets; training and export.
- **Comprehensive disease database:** 200+ diseases, 16 categories; used in extraction and reporting.
- **Documentation:** `SWAYAMSEM_README.md` (architecture, model priority, bone pipeline); `INTEGRATION_SUMMARY.md`; `SPECIALIZED_UI_README.md`; this research paper.

---

## 6. Experimental Setup and What Is Working

### 6.1 Environment

- **Python:** 3.10+.
- **Hardware:** 8GB+ RAM (16GB recommended); 10GB+ disk for model cache; optional CUDA GPU.
- **Credentials:** Hugging Face token (required for gated models); optional Groq API key for report fallback.

### 6.2 Running the System

**Streamlit UI:**
```bash
pip install -r requirements.txt
streamlit run app_specialized.py --server.port 8502
```
→ http://localhost:8502

**REST API:**
```bash
pip install -r requirements.txt
pip install -r requirements_api.txt
uvicorn api:app --reload --port 8000
```
→ http://localhost:8000; docs at http://localhost:8000/docs

**Programmatic usage:**
```python
from medical_classifier import MedicalClassifier
clf = MedicalClassifier()
# Chest
r = clf.classify_chest_xray("chest.png", generate_report=True)
# Bone
r = clf.classify_bone_xray("bone.png", generate_report=True)
# Brain
r = clf.classify_brain_tumor("brain_mri.png", generate_report=True)
# Text
r = clf.classify_text_report("Patient has pneumonia...", generate_report=False)
# General
r = clf.classify(image_path="xray.png", report_text=None, generate_report=True)
```

### 6.3 What Is Working (Verified)

- **Chest X-ray:** MedGemma + CheXpert + CXR; best-model selection; PDF/text report.
- **Bone X-ray:** MedSigLIP + MedGemma; fracture-priority selection; report; no CheXpert/CXR.
- **Brain tumor:** Custom ensemble; four-class output; report; fallback to MedSigLIP/MedGemma if custom model missing.
- **Text reports:** Disease extraction; categories; optional report.
- **General:** Multi-model classification; optional image+text; report.
- **API:** All `/api/classify*` and `/api/health` endpoints; CORS; lazy-loaded classifier.
- **UI:** All five tabs; upload; analyze; results; PDF/text download.
- **Reports:** `generate_pdf_report()`; structured layout; model results and findings.

### 6.4 Known Limitations

- MedGemma is large (~29B); optional on-demand loading; first use can be slow.
- Gated models (MedGemma, CXR) require Hugging Face access and token.
- Custom brain/chest models require `major_project-main` layout and TensorFlow.
- System is for **research and education**; not a substitute for clinical validation.

---

## 7. Discussion

SWAYAMSEM demonstrates that **modality-specific pipelines** improve clarity and correctness compared to a single generic pipeline: e.g., bone X-rays explicitly exclude chest-specific models and use fracture-priority aggregation. The **REST API** and **V0-ready specification** enable integration with modern web frontends and deployment scenarios. **Report generation** (PDF + text) and the **disease database** support interpretability and extensibility. **Fine-tuning** infrastructure allows adaptation to new datasets and use cases.

---

## 8. Conclusion

We have described **SWAYAMSEM**, a multi-modal medical AI classification system with specialized pipelines for chest X-ray, bone X-ray, brain tumor MRI, and text reports. We documented the architecture, implementation, main code components, REST API, Streamlit UI, and all current features. The system is **working** for all supported modalities, with reports, API, and UI operational. Future work may include CT/MRI expansion, multi-GPU support, Docker packaging, and formal clinical validation.

---

## References

1. Google Health AI Developer Foundations — MedSigLIP, MedGemma, CXR Foundation.  
   https://developers.google.com/health-ai-developer-foundations/

2. Hugging Face Transformers.  
   https://huggingface.co/docs/transformers

3. Stanford ML Group — CheXpert.  
   https://stanfordmlgroup.github.io/projects/chexpert/

4. FastAPI.  
   https://fastapi.tiangolo.com/

5. Streamlit.  
   https://streamlit.io/

---

## Appendix A: File Structure

```
try/
├── medical_classifier.py      # Core engine (MedicalClassifier)
├── api.py                     # FastAPI REST API
├── app_specialized.py         # Streamlit specialized UI (5 tabs)
├── app.py                     # Original Streamlit UI
├── report_generator.py        # PDF report generation
├── disease_categories.py      # 200+ diseases, 16 categories
├── fine_tune_llm.py           # LLM fine-tuning pipeline
├── requirements.txt           # Core dependencies
├── requirements_api.txt       # API dependencies (FastAPI, uvicorn, etc.)
├── SWAYAMSEM_README.md        # Architecture and user guide
├── RESEARCH_PAPER.md          # This document
├── V0_PROMPT.md               # V0 frontend spec + API contract
├── INTEGRATION_SUMMARY.md     # Brain tumor + fine-tuning integration
├── SPECIALIZED_UI_README.md   # UI tab descriptions
├── major_project-main/        # Custom brain/chest models and assets
│   ├── models/                # brainTumor, chest_xray, etc.
│   └── ...
└── ...
```

---

## Appendix B: API Response Schema (Summary)

All `POST /api/classify*` endpoints return JSON of the form:

```json
{
  "input_type": "image" | "chest_xray" | "bone_xray" | "brain_tumor" | "text_report",
  "classifications": {
    "medsiglip": { "predictions": {...}, "top_prediction": "...", "top_confidence": ... },
    "chexpert": { "top_predictions": {...} },
    "cxr": { ... },
    "medgemma": { "full_analysis": "..." },
    ...
  },
  "best_prediction": { "model": "...", "disease": "...", "confidence": ... },
  "report": "Full radiology report text...",
  "extracted_diseases": { "diseases": [...], "total_found": N }
}
```

`report` may be `null` if `generate_report` is false. `extracted_diseases` is populated mainly for text report analysis.

---

## Appendix C: Model Priority Summary

| Modality | Primary | Secondary | Tertiary | Excluded |
|----------|---------|-----------|----------|----------|
| **Chest** | MedGemma | CheXpert | CXR | — |
| **Bone** | MedSigLIP | MedGemma | — | CheXpert, CXR |
| **Brain** | Brain Tumor Ensemble | MedSigLIP | MedGemma | CheXpert, CXR |
| **Text** | Disease extraction | MedGemma | — | — |
| **General** | MedGemma | MedSigLIP, CheXpert, CXR | — | — |

---

**Document version:** 1.0  
**Last updated:** January 2025  
**Status:** Reflects current implementation and working features.
