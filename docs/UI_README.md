# Medical Classification System - Web UI

A simple web interface to test the medical disease classification system with various inputs.

## Quick Start

### Option 1: Using Batch File (Windows)
```bash
run_ui.bat
```

### Option 2: Using Command Line
```bash
streamlit run app.py
```

### Option 3: Using Shell Script (Linux/Mac)
```bash
chmod +x run_ui.sh
./run_ui.sh
```

## Features

### 📷 Image Classification Tab
- Upload medical images (PNG, JPG, JPEG, DICOM)
- View uploaded image
- Get instant disease classifications
- See predictions from all 3 models

### 📝 Text Report Tab
- Enter or paste medical report text
- Analyze text for disease patterns
- Use sample reports for testing
- Get comprehensive analysis

### 📊 View Results Tab
- See detailed predictions from all models
- View generated radiology reports
- Download results as JSON
- Download reports as text files

## Usage

1. **Start the UI**: Run `streamlit run app.py`
2. **Upload Image**: Go to "Image Classification" tab and upload a medical image
3. **Or Enter Text**: Go to "Text Report" tab and paste a medical report
4. **Click Classify**: Press the "Classify Disease" or "Analyze Report" button
5. **View Results**: See predictions in the results section or "View Results" tab

## UI Features

- ✅ **Multiple Input Methods**: Images or text reports
- ✅ **Real-time Results**: See predictions immediately
- ✅ **Detailed View**: Toggle detailed predictions
- ✅ **Report Generation**: Optional radiology report generation
- ✅ **Export Options**: Download results and reports
- ✅ **Model Information**: See which models are working
- ✅ **Sample Data**: Test with sample reports

## Tips

- **First Run**: The first classification may take 30-60 seconds to load models
- **Subsequent Runs**: Much faster as models are cached
- **Image Quality**: Better quality images = better results
- **Text Reports**: More detailed reports = better analysis

## Troubleshooting

- **UI won't start**: Make sure Streamlit is installed (`pip install streamlit`)
- **Models not loading**: Check internet connection for first-time downloads
- **Slow performance**: First run downloads models, subsequent runs are faster

## Requirements

- Python 3.8+
- Streamlit (included in requirements.txt)
- All dependencies from requirements.txt

