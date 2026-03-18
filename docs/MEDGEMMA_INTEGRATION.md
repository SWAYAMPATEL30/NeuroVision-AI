# MedGemma-27b-it Integration - Unified Medical System

## Overview

The system has been upgraded to use **MedGemma-27b-it** as the primary medical AI model for highest accuracy disease classification and professional report generation.

## MedGemma-27b-it Model

**Source:** [Google MedGemma-27b-it on Hugging Face](https://huggingface.co/google/medgemma-27b-it)

### Key Features:
- **27 Billion Parameters** - Large-scale medical AI model
- **Multimodal** - Handles both medical images and text
- **Medical-Specific Training** - Trained on medical images (X-rays, pathology, dermatology, fundus) and medical text
- **High Accuracy** - Optimized for medical reasoning and diagnosis
- **Professional Reports** - Generates comprehensive radiology reports

### Model Capabilities:
- Medical image analysis (chest X-rays, pathology, dermatology, ophthalmology)
- Medical text comprehension
- Disease diagnosis with high confidence
- Professional report generation
- Multi-modal understanding (image + text)

## System Architecture

### Primary Model (Highest Accuracy):
1. **MedGemma-27b-it** - Primary model for all classifications
   - Used for final diagnosis
   - Generates professional reports
   - Highest accuracy predictions

### Validation Models (Backup):
2. **MedSigLIP** - General detection
3. **CheXpert DenseNet** - Common diseases
4. **CXR Foundation** - Chest diseases

## How It Works

1. **Input Processing:**
   - Accepts medical images (X-rays, CT scans, etc.)
   - Accepts medical text reports
   - Can process both simultaneously

2. **Primary Analysis:**
   - MedGemma-27b-it analyzes the input
   - Provides comprehensive medical analysis
   - Extracts primary diagnosis
   - Generates detailed findings

3. **Validation:**
   - Other models run in parallel for validation
   - Results cross-checked for consistency

4. **Report Generation:**
   - Professional radiology report from MedGemma
   - Includes: Clinical Indication, Findings, Impression, Recommendations
   - PDF format available

## Usage

### Basic Usage:
```python
from medical_classifier import MedicalClassifier

classifier = MedicalClassifier()

# Classify with MedGemma (primary model)
results = classifier.classify(
    image_path="scan.jpg",
    report_text="Patient presents with...",
    generate_report=True
)

# MedGemma results
medgemma_result = results["classifications"]["medgemma"]
print(f"Primary Diagnosis: {medgemma_result['primary_diagnosis']}")
print(f"Full Analysis: {medgemma_result['full_analysis']}")

# Best prediction (always MedGemma if available)
best = results["best_prediction"]
print(f"Best Model: {best['model']}")
print(f"Disease: {best['disease']}")
```

## Model Access

**Important:** MedGemma requires accepting terms of use:
1. Visit: https://huggingface.co/google/medgemma-27b-it
2. Log in to Hugging Face
3. Accept the Health AI Developer Foundation terms
4. The model will then download automatically

## Accuracy

- **MedGemma-27b-it**: Highest accuracy (medical-grade)
- **CheXpert**: High accuracy for chest diseases
- **MedSigLIP**: General detection
- **CXR Foundation**: Chest-specialized

## Report Format

Professional radiology reports include:
- **Report Date** and model information
- **Clinical Indication**
- **Findings** (detailed analysis)
- **Impression** (primary diagnosis)
- **Recommendations**

## Benefits

✅ **Unified System** - One primary model (MedGemma) for all tasks
✅ **Highest Accuracy** - Medical-grade AI model
✅ **Professional Reports** - Proper radiology report format
✅ **Multimodal** - Handles images and text
✅ **Comprehensive** - Full medical analysis

## Notes

- First download of MedGemma may take time (~29B parameters)
- Requires GPU for best performance (CPU works but slower)
- Model automatically falls back to other models if MedGemma unavailable
- All outputs should be reviewed by qualified medical professionals

