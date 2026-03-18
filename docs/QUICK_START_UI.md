# 🚀 Quick Start - Web UI

## How to Start the UI

### Windows (Easiest)
Double-click: **`run_ui.bat`**

### Or Use Command Line
```bash
streamlit run app.py
```

The UI will open automatically in your browser at: **http://localhost:8501**

## How to Use

### 📷 Test with Images

1. Click on **"Image Classification"** tab
2. Click **"Browse files"** or drag & drop an image
3. Supported formats: PNG, JPG, JPEG
4. Click **"🔍 Classify Disease"** button
5. Wait 10-30 seconds (first time may take longer)
6. See results from all 3 models!

### 📝 Test with Text Reports

1. Click on **"Text Report"** tab
2. Type or paste a medical report
3. Or click **"📄 Load Sample 1"** or **"📄 Load Sample 2"** for examples
4. Click **"🔍 Analyze Report"** button
5. See disease classifications!

### 📊 View Detailed Results

1. Click on **"View Results"** tab
2. See all predictions from all models
3. View generated radiology report
4. Download results as JSON or text file

## Features

✅ **Upload Images** - Drag & drop or browse
✅ **Enter Text** - Paste medical reports
✅ **Sample Data** - Test with pre-loaded examples
✅ **Multiple Models** - See predictions from all 3 models
✅ **Detailed View** - Toggle detailed predictions
✅ **Export Results** - Download JSON or reports
✅ **Report Generation** - Optional radiology reports

## Tips

- **First Run**: Takes 30-60 seconds to load models
- **Subsequent Runs**: Much faster (models cached)
- **Better Images**: Higher quality = better results
- **Detailed Reports**: More text = better analysis

## Troubleshooting

**UI won't start?**
```bash
pip install streamlit
```

**Port already in use?**
```bash
streamlit run app.py --server.port 8502
```

**Models not loading?**
- Check internet connection
- First run downloads models (~280MB)
- Subsequent runs use cached models

## Example Inputs to Test

### Sample Image
- Any medical X-ray image
- Chest X-ray (best results)
- Bone X-ray
- CT scan images

### Sample Text Report 1
```
Patient presents with acute chest pain and shortness of breath.
Chest X-ray shows bilateral lower lobe opacities consistent with pneumonia.
No pneumothorax or pleural effusion noted.
Cardiomegaly is present.
```

### Sample Text Report 2
```
Patient with history of smoking, presenting with cough and fever.
Radiographic findings show right upper lobe consolidation.
Possible tuberculosis or bacterial pneumonia.
No evidence of pneumothorax.
```

## What You'll See

1. **MedSigLIP Results**: General disease detection
2. **CXR Foundation Results**: Chest-specific diseases
3. **CheXpert Results**: 14 common diseases with probabilities
4. **Generated Report**: Professional radiology report (if enabled)

Enjoy testing! 🎉




