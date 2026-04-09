"""
FastAPI backend for Medical Disease Classification System
"""
import os
import sys

# ── Load .env from same directory as this file ────────────────────────────────
# This MUST be first — before any imports that read os.getenv()
_ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
try:
    from dotenv import load_dotenv
    load_dotenv(_ENV_FILE, override=True)
    print(f"[ENV] Loaded environment from: {_ENV_FILE}")
except ImportError:
    # Fallback: manually parse the .env file if python-dotenv not installed
    if os.path.exists(_ENV_FILE):
        with open(_ENV_FILE) as _f:
            for _line in _f:
                _line = _line.strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _v = _line.split("=", 1)
                    os.environ.setdefault(_k.strip(), _v.strip())
        print(f"[ENV] Loaded environment manually from: {_ENV_FILE}")
# ─────────────────────────────────────────────────────────────────────────────

import io
import tempfile
import asyncio
from typing import Optional
from datetime import datetime

# Fix encoding on Windows
if sys.platform == "win32":
    if sys.stdout.encoding != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if sys.stderr.encoding != "utf-8":
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

HF_TOKEN = os.getenv("HF_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Lazy-load classifier (heavy models)
_classifier = None

def get_classifier():
    global _classifier
    if _classifier is None:
        os.environ["HF_TOKEN"] = HF_TOKEN or ""
        from medical_classifier import MedicalClassifier
        _classifier = MedicalClassifier()
    return _classifier


app = FastAPI(
    title="Medical Disease Classification API",
    description="AI-powered medical image and report analysis",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TextReportRequest(BaseModel):
    report_text: str
    fast_mode: bool = False


def _image_from_upload(file: UploadFile):
    from PIL import Image
    contents = file.file.read()
    return Image.open(io.BytesIO(contents)).convert("RGB")


def prepare_keras_tensor(pil_img):
    import numpy as np
    import cv2
    arr = np.array(pil_img)
    arr = cv2.resize(arr, (224, 224))
    arr = arr / 255.0
    return np.expand_dims(arr, axis=0).astype("float32")


# ── Global model cache ────────────────────────────────────────────────────────
_chest_keras_model = None
_brain_keras_model = None


# ── Gemini Report Generator (Updated for Production) ───────────────────────────
async def generate_ai_report(scan_type: str, disease: str, confidence: float,
                       patient_name: str = "Not Provided",
                       patient_age: str = "N/A",
                       patient_gender: str = "N/A",
                       patient_id: str = None,
                       extra_info: dict = None) -> str:
    """Generate a detailed, formatted clinical report using Groq (llama-3.3-70b-versatile)."""
    if not patient_id:
        import random, string
        patient_id = f"SYN-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.digits, k=4))}"
    
    if not GROQ_API_KEY:
        print("[WARN] Groq API key missing for report generation. Using fallback.")
        return f"AI Diagnosis: {disease} (Confidence: {confidence:.1f}%)"

    try:
        import httpx
        import json
        
        patient_info = f"""
Report ID: {patient_id} | Patient: {patient_name} | Age: {patient_age} | Sex: {patient_gender}
Scan: {scan_type} | AI Findings: {disease} | Confidence: {confidence:.1f}%
Date: {datetime.now().strftime('%B %d, %Y')}
"""
        prompt = f"""You are a board-certified radiologist. Generate a professional, structured clinical radiology report based on the following AI findings:
{patient_info}

The report MUST include these sections:
1. PATIENT DEMOGRAPHICS
2. CLINICAL INDICATION
3. TECHNIQUE
4. FINDINGS (Provide detailed, clinical paragraphs describing the findings for {disease})
5. IMPRESSION (Summary of the diagnosis)
6. RECOMMENDATIONS

Use formal medical terminology. Ensure the tone is professional and clinical.
Include a standard radiological disclaimer at the end."""

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # List of models to try in order of preference
        models_to_try = [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
            "mixtral-8x7b-32768",
            "llama3-70b-8192"
        ]
        
        last_error = "Unknown error"
        async with httpx.AsyncClient() as client:
            for model in models_to_try:
                try:
                    payload = {
                        "model": model,
                        "messages": [
                            {"role": "system", "content": "You are a specialized medical documentation AI for NeuroVision AI."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3, # Lower temperature for clinical consistency
                        "max_tokens": 1500
                    }
                    print(f"[AI] Calling Groq API with model {model} for Report: {patient_name}...")
                    resp = await client.post(url, headers=headers, json=payload, timeout=30.0)
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        print(f"[AI] Groq Report Generated Successfully (Model: {model}).")
                        return data['choices'][0]['message']['content']
                    else:
                        print(f"[WARN] Groq model {model} failed: {resp.status_code}")
                        last_error = f"Groq API {resp.status_code}: {resp.text}"
                except Exception as e:
                    print(f"[WARN] Groq model {model} exception: {str(e)}")
                    last_error = str(e)
            
            raise Exception(f"All Groq models failed. Last error: {last_error}")

    except Exception as e:
        print(f"[ERROR] Groq Report Generation failed: {str(e)}")
        return f"AI Diagnosis: {disease} (Confidence: {confidence:.1f}%)\n\nPreliminary analysis finalized. (Note: Detailed AI report generation encountered an error: {str(e)})"



# ── Supabase Integration ──────────────────────────────────────────────────────
async def save_to_supabase(data: dict):
    """Save analysis results to Supabase diagnostic_reports table."""
    try:
        import httpx
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not supabase_key:
            print("[WARN] Supabase not configured for auto-save.")
            return

        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{supabase_url}/rest/v1/diagnostic_reports",
                headers=headers,
                json=data
            )
            if resp.status_code >= 400:
                print(f"[ERROR] Supabase save failed: {resp.status_code} - {resp.text}")
            else:
                print("[SUCCESS] Report saved to Supabase.")
    except Exception as e:
        print(f"[ERROR] Supabase integration error: {e}")


def _fallback_report(scan_type: str, disease: str, confidence: float,
                     patient_name: str = "Not Provided",
                     patient_age: str = "N/A",
                     patient_gender: str = "N/A",
                     patient_id: str = "N/A") -> str:
    """Fallback template report if OpenAI is unavailable."""
    date = datetime.now().strftime('%B %d, %Y at %H:%M')
    return f"""CLINICAL RADIOLOGY REPORT
{'='*60}

PATIENT DEMOGRAPHICS
--------------------
Patient Name:   {patient_name}
Age:            {patient_age}
Gender:         {patient_gender}
Report ID:      {patient_id}
Study Date:     {date}
Facility:       NeuroVision AI Diagnostics Center
Referring:      AI-Assisted Screening System

CLINICAL INDICATION
-------------------
AI-assisted analysis of {scan_type.lower()} imaging study for
diagnostic screening of {patient_name}, {patient_age}, {patient_gender}.

TECHNIQUE
---------
Digital image analysis using deep learning neural network ensemble
(InceptionV3/ResNet50/DenseNet architecture).
Processing: NeuroVision AI v1.0 — Automated Diagnostic Pipeline.

FINDINGS
--------
The AI analysis of the submitted {scan_type.lower()} identified findings
most consistent with:

  Primary Diagnosis:  {disease}
  Confidence Level:   {confidence:.1f}%
  Classification:     {'High' if confidence > 80 else 'Moderate' if confidence > 60 else 'Low'} Confidence

{'  NOTE: High confidence finding (>70%) - clinical correlation recommended.' if confidence > 70 else '  NOTE: Moderate confidence - additional imaging may be warranted.'}

IMPRESSION
----------
AI screening of {patient_name}'s {scan_type.lower()} indicates radiological
patterns consistent with {disease} (confidence: {confidence:.1f}%).
{'This finding warrants prompt clinical attention.' if confidence > 80 else 'Correlation with clinical history is advised.'}

RECOMMENDATIONS
---------------
1. Clinical correlation with {patient_name}'s medical history is strongly advised.
2. Findings should be verified by a board-certified radiologist.
3. Additional diagnostic workup may be warranted based on clinical presentation.
4. Follow-up imaging recommended in 4-6 weeks if findings are new.
5. This AI analysis serves as a preliminary screening tool only.

QUALITY ASSURANCE
-----------------
AI Model Confidence: {confidence:.1f}% — {'Meets diagnostic threshold.' if confidence > 70 else 'Below standard threshold; additional review required.'}
Processed by: NeuroVision AI v1.0
Report generated: {date}

---
DISCLAIMER: This report is generated by an AI system and is intended
for informational and screening purposes only. It does not constitute
a confirmed medical diagnosis. All findings must be reviewed and
validated by a qualified, licensed healthcare professional before any
clinical decisions are made.

Signed: NeuroVision AI Diagnostic System
Report ID: {patient_id}
"""


def generate_pdf_bytes(report_text: str, title: str, disease: str, confidence: float,
                       patient_name: str = "Not Provided",
                       patient_age: str = "N/A",
                       patient_gender: str = "N/A",
                       patient_id: str = "N/A") -> bytes:
    """Generate a professional PDF from the report text."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch, cm
        from reportlab.lib.colors import HexColor, black, white, grey
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm,
        )

        styles = getSampleStyleSheet()
        
        # Custom styles
        navy = HexColor('#0A1628')
        teal = HexColor('#00B4D8')
        lightgrey = HexColor('#F8F9FA')
        darkgrey = HexColor('#495057')
        medblue = HexColor('#1E3A5F')
        
        title_style = ParagraphStyle(
            'CustomTitle', parent=styles['Normal'],
            fontSize=22, textColor=white, fontName='Helvetica-Bold',
            spaceAfter=4, alignment=TA_CENTER
        )
        subtitle_style = ParagraphStyle(
            'Subtitle', parent=styles['Normal'],
            fontSize=10, textColor=HexColor('#ADB5BD'), fontName='Helvetica',
            alignment=TA_CENTER
        )
        section_style = ParagraphStyle(
            'Section', parent=styles['Normal'],
            fontSize=11, textColor=teal, fontName='Helvetica-Bold',
            spaceBefore=14, spaceAfter=6
        )
        body_style = ParagraphStyle(
            'Body', parent=styles['Normal'],
            fontSize=9.5, textColor=darkgrey, fontName='Helvetica',
            leading=14, spaceAfter=6
        )
        label_style = ParagraphStyle(
            'Label', parent=styles['Normal'],
            fontSize=8, textColor=HexColor('#6C757D'), fontName='Helvetica-Bold',
        )
        value_style = ParagraphStyle(
            'Value', parent=styles['Normal'],
            fontSize=10, textColor=navy, fontName='Helvetica-Bold',
        )
        disclaimer_style = ParagraphStyle(
            'Disclaimer', parent=styles['Normal'],
            fontSize=7.5, textColor=HexColor('#868E96'), fontName='Helvetica-Oblique',
            alignment=TA_CENTER, leading=11
        )

        story = []

        # ── Header Banner ──────────────────────────────────────────────────────────────
        header_data = [
            [Paragraph('NeuroVision AI', title_style)],
            [Paragraph('AI-Powered Clinical Diagnostic Report', subtitle_style)],
        ]
        header_table = Table(header_data, colWidths=[18*cm])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), navy),
            ('PADDING', (0,0), (-1,-1), 16),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ROUNDEDCORNERS', [8,8,8,8]),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 0.4*cm))

        # ── Patient Demographics Box ─────────────────────────────────────────────────
        pat_data = [
            [
                Paragraph('<b>Patient Name</b>', label_style),
                Paragraph('<b>Age</b>', label_style),
                Paragraph('<b>Gender</b>', label_style),
                Paragraph('<b>Report ID</b>', label_style),
            ],
            [
                Paragraph(f'{patient_name}', value_style),
                Paragraph(f'{patient_age}', value_style),
                Paragraph(f'{patient_gender}', value_style),
                Paragraph(f'{patient_id}', value_style),
            ],
        ]
        pat_table = Table(pat_data, colWidths=[5.5*cm, 3.5*cm, 3.5*cm, 5.5*cm])
        pat_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#E8EDF2')),
            ('BACKGROUND', (0,1), (-1,1), white),
            ('GRID', (0,0), (-1,-1), 0.5, HexColor('#DEE2E6')),
            ('PADDING', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ROUNDEDCORNERS', [6,6,6,6]),
        ]))
        story.append(pat_table)
        story.append(Spacer(1, 0.3*cm))

        # ── Diagnosis Summary Box ───────────────────────────────────────────────────
        conf_color = HexColor('#28A745') if confidence >= 70 else HexColor('#FFC107') if confidence >= 50 else HexColor('#DC3545')
        conf_label = 'HIGH' if confidence >= 70 else 'MODERATE' if confidence >= 50 else 'LOW'
        summary_data = [
            [
                Paragraph(f'<b>Primary Diagnosis</b><br/><font size=14>{disease}</font>', 
                         ParagraphStyle('SD', fontName='Helvetica', fontSize=9.5, textColor=navy, alignment=TA_CENTER)),
                Paragraph(f'<b>Confidence</b><br/><font size=14 color="{conf_color.hexval()}">{confidence:.1f}%</font><br/><font size=7 color="{conf_color.hexval()}">{conf_label}</font>',
                         ParagraphStyle('SC', fontName='Helvetica', fontSize=9.5, textColor=navy, alignment=TA_CENTER)),
                Paragraph(f'<b>Report Date</b><br/><font size=10>{datetime.now().strftime("%d %b %Y")}</font><br/><font size=7>{datetime.now().strftime("%H:%M IST")}</font>',
                         ParagraphStyle('SR', fontName='Helvetica', fontSize=9.5, textColor=navy, alignment=TA_CENTER)),
                Paragraph(f'<b>System</b><br/><font size=10>NeuroVision AI v1.0</font><br/><font size=7>Neural Ensemble</font>',
                         ParagraphStyle('SM', fontName='Helvetica', fontSize=9.5, textColor=navy, alignment=TA_CENTER)),
            ]
        ]
        summary_table = Table(summary_data, colWidths=[5.5*cm, 4*cm, 4*cm, 4.5*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), lightgrey),
            ('GRID', (0,0), (-1,-1), 0.5, HexColor('#DEE2E6')),
            ('PADDING', (0,0), (-1,-1), 12),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ROUNDEDCORNERS', [6,6,6,6]),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.5*cm))

        # ── Report Body ──────────────────────────────────────────────────────────────
        story.append(HRFlowable(width="100%", thickness=1.5, color=medblue))
        story.append(Paragraph('DETAILED CLINICAL REPORT', section_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#DEE2E6')))
        story.append(Spacer(1, 0.2*cm))

        for line in report_text.split('\n'):
            line = line.strip()
            if not line:
                story.append(Spacer(1, 0.15*cm))
                continue
            if line.isupper() and len(line) < 60:
                story.append(Paragraph(line, section_style))
            elif line.startswith('---') or line.startswith('==='):
                story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#DEE2E6')))
            else:
                story.append(Paragraph(line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), body_style))

        story.append(Spacer(1, 0.6*cm))
        story.append(HRFlowable(width="100%", thickness=1.5, color=medblue))
        story.append(Spacer(1, 0.3*cm))

        # ── Footer ─────────────────────────────────────────────────────────────────
        story.append(Paragraph(
            'DISCLAIMER: This report is generated by an AI system and is intended '
            'for informational and screening purposes only. It does not constitute a confirmed '
            'medical diagnosis. All findings must be reviewed and validated by a qualified, '
            'licensed healthcare professional before any clinical decisions are made.',
            disclaimer_style
        ))
        story.append(Spacer(1, 0.15*cm))
        story.append(Paragraph(
            f'Generated by NeuroVision AI \u2022 {datetime.now().strftime("%d %B %Y, %H:%M")} '
            f'\u2022 Report ID: {patient_id} \u2022 CONFIDENTIAL',
            disclaimer_style
        ))

        doc.build(story)
        buffer.seek(0)
        return buffer.read()

    except ImportError:
        # Fallback: return plain text as bytes if reportlab not installed
        return report_text.encode('utf-8')


# ── Brain model loader ────────────────────────────────────────────────────────
def _load_brain_model():
    import tensorflow as tf
    import h5py
    from tensorflow.keras.applications import InceptionV3
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
    from tensorflow.keras import regularizers

    MODEL_PATH = "major_project-main/models/inception_model.h5"
    print("[Brain] Reconstructing model architecture...")
    base_model = InceptionV3(weights=None, include_top=False, input_shape=(224, 224, 3))
    model = Sequential([
        base_model,
        Conv2D(128, (3, 3), activation="relu", padding="same"),
        MaxPooling2D((2, 2)),
        Conv2D(64, (3, 3), activation="relu", padding="same"),
        MaxPooling2D((2, 2)),
        Flatten(),
        Dense(512, activation="relu", kernel_regularizer=regularizers.l2(0.001)),
        Dropout(0.5),
        Dense(256, activation="relu", kernel_regularizer=regularizers.l2(0.001)),
        Dropout(0.5),
        Dense(4, activation="softmax")
    ])
    model.build((None, 224, 224, 3))

    print(f"[Brain] Loading weights from {MODEL_PATH}...")
    with h5py.File(MODEL_PATH, "r") as f:
        wg = f["model_weights"] if "model_weights" in f else f
        loaded = 0
        for layer in model.layers:
            name = layer.name
            if name not in wg:
                continue
            ld = wg[name]
            wnames = ld.attrs.get("weight_names", [])
            if not len(wnames):
                continue
            weights = []
            for wn in wnames:
                wn_str = wn.decode() if isinstance(wn, bytes) else wn
                key = wn_str.split("/")[-1]
                if key in ld:
                    weights.append(ld[key][()])
                elif wn_str in ld:
                    weights.append(ld[wn_str][()])
            if weights:
                try:
                    layer.set_weights(weights)
                    loaded += 1
                except Exception as e:
                    print(f"  [Brain] Skipping {name}: {e}")
    print(f"[Brain] Loaded weights for {loaded} layers. Ready!")
    return model


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok", "message": "Medical Classification API is running"}


@app.post("/api/classify")
async def classify(
    image: Optional[UploadFile] = File(None),
    report_text: Optional[str] = Form(None),
    generate_report: bool = Form(True),
    use_comprehensive: bool = Form(False),
    fast_mode: bool = Form(False),
    patient_name: str = Form("Not Provided"),
    patient_age: str = Form("N/A"),
    patient_gender: str = Form("N/A")
):
    if not image and not report_text:
        raise HTTPException(400, "Provide either 'image' or 'report_text'")
    clf = get_classifier()
    image_path = _image_from_upload(image) if image else None
    result = clf.classify(
        image_path=image_path,
        report_text=report_text or None,
        generate_report=generate_report,
        use_comprehensive=use_comprehensive,
        fast_mode=fast_mode
    )

    # Auto-save report to Supabase
    import random, string
    report_id = f"SYN-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.digits, k=4))}"
    
    # We use asyncio.create_task to not block the response
    report_data = {
        "id": report_id,
        "patientName": patient_name,
        "patientAge": str(patient_age),
        "patientGender": patient_gender,
        "scanType": "General Analysis" if not report_text else "Text Report",
        "disease": result.get("disease", "Unknown"),
        "confidence": float(result.get("confidence", 0)),
        "reportText": result.get("report", ""),
        "classifications": result.get("classifications", {}),
    }
    asyncio.create_task(save_to_supabase(report_data))
    
    return result


def _load_chest_model():
    import tensorflow as tf
    import h5py
    from tensorflow.keras.layers import Input, Conv2D, BatchNormalization, ReLU, Concatenate, GlobalAveragePooling2D, Dense, AveragePooling2D, MaxPooling2D
    from tensorflow.keras.models import Model

    MODEL_PATH = "major_project-main/models/chest_xray_finetuned.h5"
    print("[Chest] Reconstructing model architecture (CustomNet121)...")
    
    def conv_block(x, growth_rate):
        x1 = BatchNormalization()(x)
        x1 = ReLU()(x1)
        x1 = Conv2D(filters=growth_rate, kernel_size=(3, 3), padding='same')(x1)
        x = Concatenate()([x, x1])
        return x

    def dense_block(x, num_layers, growth_rate):
        for _ in range(num_layers):
            x = conv_block(x, growth_rate)
        return x

    def transition_block(x, reduction):
        x = BatchNormalization()(x)
        x = ReLU()(x)
        x = Conv2D(int(tf.keras.backend.int_shape(x)[-1] * reduction), kernel_size=(1, 1), padding='same')(x)
        x = AveragePooling2D((2, 2), strides=(2, 2))(x)
        return x

    def CustomNet121(input_shape=(224, 224, 3), num_classes=11, growth_rate=32, num_blocks=[6, 12, 24, 16], reduction=0.5):
        inputs = Input(shape=input_shape)
        x = Conv2D(64, kernel_size=(7, 7), strides=(2, 2), padding='same')(inputs)
        x = BatchNormalization()(x)
        x = ReLU()(x)
        x = MaxPooling2D(pool_size=(3, 3), strides=(2, 2), padding='same')(x)

        for i, num_layers in enumerate(num_blocks):
            x = dense_block(x, num_layers, growth_rate)
            if i != len(num_blocks) - 1:
                x = transition_block(x, reduction)

        x = BatchNormalization()(x)
        x = ReLU()(x)
        x = GlobalAveragePooling2D()(x)
        x = Dense(num_classes, activation='softmax')(x)
        return Model(inputs, x)

    model = CustomNet121(num_classes=11)
    model.build((None, 224, 224, 3))

    print(f"[Chest] Loading weights from {MODEL_PATH} manually...")
    try:
        with h5py.File(MODEL_PATH, "r") as f:
            wg = f["model_weights"] if "model_weights" in f else f
            loaded = 0
            for layer in model.layers:
                name = layer.name
                if name not in wg: continue
                ld = wg[name]
                wnames = ld.attrs.get("weight_names", [])
                if not len(wnames): continue
                weights = []
                for wn in wnames:
                    wn_str = wn.decode() if isinstance(wn, bytes) else wn
                    key = wn_str.split("/")[-1]
                    if key in ld: weights.append(ld[key][()])
                    elif wn_str in ld: weights.append(ld[wn_str][()])
                if weights:
                    try:
                        layer.set_weights(weights)
                        loaded += 1
                    except Exception: pass
        print(f"[Chest] Manual load complete ({loaded} layers). Ready!")
    except Exception as e:
        print(f"[Chest] Manual load failed: {e}. Falling back to default load_model.")
        model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    
    return model


@app.post("/api/classify/chest")
async def classify_chest(
    image: UploadFile = File(...),
    generate_report: bool = Form(True),
    fast_mode: bool = Form(False),
    patient_name: str = Form("Not Provided"),
    patient_age: str = Form("N/A"),
    patient_gender: str = Form("N/A")
):
    global _chest_keras_model
    img = _image_from_upload(image)
    try:
        import numpy as np
        if _chest_keras_model is None: _chest_keras_model = _load_chest_model()
        tensor = prepare_keras_tensor(img)
        prediction = _chest_keras_model.predict(tensor, verbose=0)
        idx = int(np.argmax(prediction[0]))
        confidence = float(np.max(prediction[0])) * 100
        labels = ["Atelectasis", "Cardiomegaly", "Consolidation", "Effusion", "Hernia", "Infiltration", "Mass", "No Finding", "Nodule", "Pneumonia", "Pneumothorax"]
        disease = labels[idx] if idx < len(labels) else "Unknown"
        report = ""
        if generate_report:
            report = await generate_ai_report(
                scan_type="Chest X-Ray",
                disease=disease,
                confidence=confidence,
                patient_name=patient_name,
                patient_age=patient_age,
                patient_gender=patient_gender
            )
        res = {
            "disease": disease, "confidence": round(confidence, 2), "report": report,
            "model_used": "CustomNet121 Ensemble",
            "patient_info": {"name": patient_name, "age": patient_age, "gender": patient_gender}
        }
        
        # Auto-save to Supabase
        import random, string
        report_id = f"SYN-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.digits, k=4))}"
        asyncio.create_task(save_to_supabase({
            "id": report_id,
            "patientName": patient_name,
            "patientAge": str(patient_age),
            "patientGender": patient_gender,
            "scanType": "Chest X-Ray",
            "disease": disease,
            "confidence": float(confidence),
            "reportText": report,
        }))
        
        return res
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(500, f"Chest model inference failed: {str(e)}")


@app.post("/api/classify/brain")
async def classify_brain(
    image: UploadFile = File(...),
    generate_report: bool = Form(True),
    fast_mode: bool = Form(False),
    patient_name: str = Form("Not Provided"),
    patient_age: str = Form("N/A"),
    patient_gender: str = Form("N/A")
):
    global _brain_keras_model
    img = _image_from_upload(image)
    try:
        import numpy as np
        if _brain_keras_model is None: _brain_keras_model = _load_brain_model()
        tensor = prepare_keras_tensor(img)
        prediction = _brain_keras_model.predict(tensor, verbose=0)
        idx = int(np.argmax(prediction[0]))
        confidence = float(np.max(prediction[0])) * 100
        labels = ["Glioma", "Meningioma", "No Tumor", "Pituitary"]
        disease = labels[idx] if idx < len(labels) else "Unknown"
        report = ""
        if generate_report:
            report = await generate_ai_report(
                scan_type="Brain MRI",
                disease=disease,
                confidence=confidence,
                patient_name=patient_name,
                patient_age=patient_age,
                patient_gender=patient_gender
            )
        res = {
            "disease": disease, "confidence": round(confidence, 2), "report": report,
            "model_used": "InceptionV3 Brain Tumor Model",
            "patient_info": {"name": patient_name, "age": patient_age, "gender": patient_gender}
        }

        # Auto-save to Supabase
        import random, string
        report_id = f"SYN-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.digits, k=4))}"
        asyncio.create_task(save_to_supabase({
            "id": report_id,
            "patientName": patient_name,
            "patientAge": str(patient_age),
            "patientGender": patient_gender,
            "scanType": "Brain MRI",
            "disease": disease,
            "confidence": float(confidence),
            "reportText": report,
        }))

        return res
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(500, f"Brain model inference failed: {str(e)}")


@app.post("/api/classify/bone")
async def classify_bone(
    image: UploadFile = File(...),
    generate_report: bool = Form(True),
    fast_mode: bool = Form(False),
):
    clf = get_classifier()
    img = _image_from_upload(image)
    result = clf.classify_bone_xray(image_path=img, generate_report=generate_report, fast_mode=fast_mode)
    
    # Enhance with report
    if generate_report:
        disease = result.get("disease", result.get("top_prediction", "Unknown"))
        confidence = result.get("confidence", result.get("top_confidence", 0))
        if isinstance(confidence, float) and confidence <= 1:
            confidence *= 100
        result["report"] = await generate_ai_report("Bone X-Ray", str(disease), float(confidence))
    
    return result


@app.post("/api/classify/text")
async def classify_text(req: TextReportRequest):
    clf = get_classifier()
    result = clf.classify_text_report(
        report_text=req.report_text, generate_report=False, fast_mode=req.fast_mode
    )
    return result


# ── PDF Report Download ───────────────────────────────────────────────────────

@app.post("/api/report/download")
async def download_report(
    scan_type: str = Form(...),
    disease: str = Form(...),
    confidence: float = Form(...),
    report_text: Optional[str] = Form(None),
    patient_name: Optional[str] = Form("Not Provided"),
    patient_age: Optional[str] = Form("N/A"),
    patient_gender: Optional[str] = Form("N/A"),
):
    """Generate and return a professional PDF report for download."""
    try:
        import random, string
        patient_id = f"SYN-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.digits, k=4))}"

        # Generate AI report if not provided
        if not report_text:
            report_text = await generate_ai_report(
                scan_type, disease, confidence,
                patient_name=patient_name or "Not Provided",
                patient_age=patient_age or "N/A",
                patient_gender=patient_gender or "N/A",
                patient_id=patient_id,
            )

        pdf_bytes = generate_pdf_bytes(
            report_text, f"{scan_type} Report", disease, confidence,
            patient_name=patient_name or "Not Provided",
            patient_age=patient_age or "N/A",
            patient_gender=patient_gender or "N/A",
            patient_id=patient_id,
        )
        
        filename = f"NeuroVision AI_Medical_Report_{scan_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(500, f"PDF generation failed: {str(e)}")


@app.post("/api/report/pdf")
async def get_pdf_report_legacy(results: dict):
    """Legacy PDF endpoint."""
    disease = results.get("disease", "Unknown")
    confidence = results.get("confidence", 0)
    scan_type = results.get("scan_type", "Medical Scan")
    report_text = results.get("report", "")
    if not report_text:
        report_text = await generate_ai_report(scan_type, disease, confidence)
    pdf_bytes = generate_pdf_bytes(report_text, f"{scan_type} Report", disease, confidence)
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    with open(path, "wb") as f:
        f.write(pdf_bytes)
    return FileResponse(path, filename="medical_report.pdf", media_type="application/pdf")


# ── AI Chat Support (Groq Implementation) ──────────────────────────────────────
@app.post("/api/ai/chat")
async def ai_chat(
    message: str = Form(...),
    history: Optional[str] = Form("[]"),
    system_prompt: Optional[str] = Form("You are a helpful AI assistant for NeuroVision AI."),
):
    """
    Direct AI chat endpoint using Groq (llama-3.3-70b-versatile).
    This replaces the legacy OpenAI chatbot implementation.
    """
    if not GROQ_API_KEY:
        print("[AI] Groq API key missing. Using fallback response.")
        return {"response": "I'm sorry, my AI backend (Groq) is not configured. please set GROQ_API_KEY."}

    try:
        import httpx
        import json
        
        print(f"[AI] Incoming Chat: {message[:50]}...")
        print("[AI] Using Provider: Groq (llama-3.3-70b-versatile)")

        # Parse history
        try:
            chat_history = json.loads(history)
        except:
            chat_history = []

        # Prepare payload for Groq (OpenAI-compatible format)
        messages = [{"role": "system", "content": system_prompt}]
        for turn in chat_history[-5:]: # Keep last 5 turns for context
            messages.append({"role": turn.get("role", "user"), "content": turn.get("text", turn.get("content", ""))})
        messages.append({"role": "user", "content": message})
        
        # List of models to try in order of preference for chat
        models_to_try = [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ]
        
        last_error = "Unknown error"
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            for model in models_to_try:
                try:
                    payload = {
                        "model": model,
                        "messages": messages,
                        "max_tokens": 1000,
                        "temperature": 0.7
                    }
                    resp = await client.post(url, headers=headers, json=payload, timeout=20.0)
                    if resp.status_code == 200:
                        data = resp.json()
                        return {"response": data['choices'][0]['message']['content']}
                    else:
                        print(f"[WARN] Groq chat model {model} failed: {resp.status_code}")
                        last_error = f"Groq API {resp.status_code}"
                except Exception as e:
                    print(f"[WARN] Groq chat model {model} exception: {str(e)}")
                    last_error = str(e)
            
            raise Exception(f"All Groq chat models failed. Last error: {last_error}")

    except Exception as e:
        print(f"AI Chat error: {e}")
        return {"response": "I'm having a brief connection issue with my AI core. I can still help you with basic questions, but for complex medical analysis, please try again in a few minutes."}



@app.post("/analyze-scores")
async def analyze_scores(data: dict):
    """
    Analyze mental health assessment scores and generate a personalized plan.
    """
    try:
        phq9 = data.get("phq9", 0)
        phq12 = data.get("phq12", 0)
        gad7 = data.get("gad7", 0)
        user_prompt = data.get("userPrompt", "")

        # 1. Interpret scores (Clinical mapping)
        def interpret_phq9(s):
            if s >= 20: return {"score": s, "interpretation": "Severe Depression", "severity_level": "severe", "color": "destructive"}
            if s >= 15: return {"score": s, "interpretation": "Moderately Severe Depression", "severity_level": "moderate-severe", "color": "warning"}
            if s >= 10: return {"score": s, "interpretation": "Moderate Depression", "severity_level": "moderate", "color": "warning"}
            if s >= 5: return {"score": s, "interpretation": "Mild Depression", "severity_level": "mild", "color": "secondary"}
            return {"score": s, "interpretation": "Minimal Depression", "severity_level": "minimal", "color": "outline"}

        def interpret_gad7(s):
            if s >= 15: return {"score": s, "interpretation": "Severe Anxiety", "severity_level": "severe", "color": "destructive"}
            if s >= 10: return {"score": s, "interpretation": "Moderate Anxiety", "severity_level": "moderate", "color": "warning"}
            if s >= 5: return {"score": s, "interpretation": "Mild Anxiety", "severity_level": "mild", "color": "secondary"}
            return {"score": s, "interpretation": "Minimal Anxiety", "severity_level": "minimal", "color": "outline"}

        def interpret_phq12(s):
            if s >= 15: return {"score": s, "interpretation": "High Somatic Symptoms", "severity_level": "severe", "color": "destructive"}
            if s >= 10: return {"score": s, "interpretation": "Medium Somatic Symptoms", "severity_level": "moderate", "color": "warning"}
            return {"score": s, "interpretation": "Low Somatic Symptoms", "severity_level": "minimal", "color": "outline"}

        scores_summary = {
            "phq9": interpret_phq9(phq9),
            "gad7": interpret_gad7(gad7),
            "phq12": interpret_phq12(phq12)
        }

        # Determine overall severity
        max_score = max(phq9/27, gad7/21, phq12/24)
        overall = "minimal"
        if max_score > 0.8: overall = "critical"
        elif max_score > 0.6: overall = "severe"
        elif max_score > 0.4: overall = "moderate"
        elif max_score > 0.2: overall = "mild"

        # 2. Generate Recommendations via AI
        import json
        import httpx
        
        system_msg = "You are an AI Mental Health Assistant. Based on PHQ-9, GAD-7, and PHQ-12 scores, generate a structured JSON recommendation plan."
        prompt = f"""
        User Scores: PHQ-9 (Depression): {phq9}/27, GAD-7 (Anxiety): {gad7}/21, PHQ-12 (Somatic): {phq12}/24.
        User Input: {user_prompt}
        
        Generate a personalized plan. Return ONLY a JSON object with this exact structure:
        {{
            "recommendation_sections": [
                {{ "title": "Priority Steps", "content": ["step 1", "step 2"], "priority": "high", "icon": "alert" }},
                {{ "title": "Lifestyle Changes", "content": ["..."], "priority": "medium", "icon": "lifestyle" }}
            ],
            "requires_immediate_attention": true/false (true if any score is severe),
            "crisis_resources": ["Optional crisis number if needed"]
        }}
        """

        plan = {
            "recommendation_sections": [
                { "title": "Initial Assessment", "content": ["Your scores indicate " + scores_summary["phq9"]["interpretation"] + "."], "priority": "medium", "icon": "assessment" },
                { "title": "General Wellness", "content": ["Focus on consistent sleep and hydration."], "priority": "low", "icon": "lifestyle" }
            ],
            "requires_immediate_attention": max_score > 0.7,
            "crisis_resources": ["988 Suicide & Crisis Lifeline"] if max_score > 0.7 else []
        }

        if GROQ_API_KEY:
            try:
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
                payload = {
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": prompt}
                    ],
                    "response_format": {"type": "json_object"}
                }
                async with httpx.AsyncClient() as client:
                    resp = await client.post(url, headers=headers, json=payload, timeout=20.0)
                    if resp.status_code == 200:
                        ai_data = resp.json()
                        content = json.loads(ai_data['choices'][0]['message']['content'])
                        plan.update(content)
            except Exception as e:
                print(f"[AI] Error in score analysis: {e}")

        return {
            "success": True,
            "scores": scores_summary,
            "overall_severity": overall,
            **plan
        }

    except Exception as e:
        import traceback; traceback.print_exc()
        return {"success": False, "error": str(e)}


@app.get("/download-eeg-report/{user_id}")
async def download_eeg_report(user_id: str):
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    with open(path, "wb") as f:
        f.write(b"%PDF-1.4\n1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 100 100]>> endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000056 00000 n\n0000000111 00000 n\ntrailer <</Size 4 /Root 1 0 R>>\nstartxref\n190\n%%EOF\n")
    return FileResponse(path, filename=f"eeg_report_{user_id}.pdf", media_type="application/pdf")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
