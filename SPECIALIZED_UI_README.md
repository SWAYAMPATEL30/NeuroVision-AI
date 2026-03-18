# Specialized Medical Classification UI

## Overview

A specialized UI divided by medical imaging types, using the best models for each category to ensure accurate results without errors.

## UI Structure

### 🫁 Tab 1: Chest X-Ray
**Best Models:**
- **MedGemma-27b-it** (Primary - Highest Accuracy)
- **CheXpert DenseNet** (Chest Disease Specialist)
- **CXR Foundation** (Chest X-Ray Specialized)

**Best For:**
- Pneumonia
- Pneumothorax
- Cardiomegaly
- Lung diseases
- Chest abnormalities

### 🦴 Tab 2: Bone X-Ray
**Best Models:**
- **MedGemma-27b-it** (Primary - Highest Accuracy)
- **MedSigLIP** (Fracture & Bone Abnormality Detection)

**Best For:**
- Fractures
- Broken bones
- Dislocations
- Bone tumors
- Osteoporosis
- Arthritis

### 📝 Tab 3: Medical Reports
**Best Models:**
- **MedGemma-27b-it** (Primary - Text Analysis)
- **Text Disease Extraction** (Comprehensive database)

**Best For:**
- Medical report analysis
- Disease extraction from text
- Clinical note interpretation

### 🔬 Tab 4: General Analysis
**Best Models:**
- **MedGemma-27b-it** (Primary)
- **MedSigLIP** (Comprehensive Detection)

**Best For:**
- Any medical image type
- Combined image + text analysis
- General medical analysis

## Model Selection Strategy

### MedGemma-27b-it Usage:
- **Primary model** for all categories
- Highest accuracy medical AI
- Used for final diagnosis
- Generates professional reports

### MedSigLIP Usage:
- **Bone X-rays**: Fracture detection
- **General Analysis**: Comprehensive disease detection
- Zero-shot classification

### CheXpert + CXR Usage:
- **Chest X-rays only**: Specialized chest disease detection
- High accuracy for pulmonary/cardiac findings

## Benefits

✅ **No Errors**: Each category uses appropriate models
✅ **Best Accuracy**: MedGemma for primary, specialized models for validation
✅ **Proper Routing**: Inputs go to right models automatically
✅ **Professional Reports**: Generated from best model
✅ **PDF Export**: Available for all reports

## Usage

### Start the Specialized UI:
```bash
streamlit run app_specialized.py
```

Or access at: http://localhost:8502

### Workflow:
1. Select appropriate tab for your input type
2. Upload image or enter text
3. Click analyze
4. Get results from best models
5. Download PDF report

## Model Priority

1. **MedGemma-27b-it** - Always primary (if available)
2. **Specialized models** - Category-specific (CheXpert for chest, MedSigLIP for bones)
3. **Fallback models** - If primary unavailable

## Notes

- MedGemma requires accepting terms at Hugging Face
- Each category optimized for its specific use case
- No mixing of incompatible models
- Best model automatically selected for final output

