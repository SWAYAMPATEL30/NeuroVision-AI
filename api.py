"""
FastAPI backend for Medical Disease Classification System
Exposes REST endpoints for the V0 frontend to call.
Run: uvicorn api:app --reload --port 8000
"""

import os
import io
import sys
from typing import Optional

# Fix encoding on Windows
if sys.platform == "win32":
    import io as _io
    if sys.stdout.encoding != "utf-8":
        sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if sys.stderr.encoding != "utf-8":
        sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Lazy-load classifier (heavy models)
_classifier = None

def get_classifier():
    global _classifier
    if _classifier is None:
        from medical_classifier import MedicalClassifier
        _classifier = MedicalClassifier()
    return _classifier


app = FastAPI(
    title="Medical Disease Classification API",
    description="AI-powered medical image and report analysis",
    version="1.0.0",
)

# CORS: allow V0/Next.js frontend (localhost:3000, Vercel, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TextReportRequest(BaseModel):
    report_text: str


def _image_from_upload(file: UploadFile):
    from PIL import Image
    contents = file.file.read()
    return Image.open(io.BytesIO(contents)).convert("RGB")


@app.post("/api/classify")
async def classify_general(
    image: Optional[UploadFile] = File(None),
    report_text: Optional[str] = Form(None),
    generate_report: bool = Form(True),
):
    """General classification: any image + optional report text."""
    if not image and not report_text:
        raise HTTPException(400, "Provide either 'image' or 'report_text'")
    clf = get_classifier()
    image_path = None
    if image:
        img = _image_from_upload(image)
        image_path = img
    result = clf.classify(
        image_path=image_path,
        report_text=report_text or None,
        generate_report=generate_report,
    )
    return result


@app.post("/api/classify/chest")
async def classify_chest(
    image: UploadFile = File(...),
    generate_report: bool = Form(True),
):
    """Chest X-ray specialized classification."""
    clf = get_classifier()
    img = _image_from_upload(image)
    result = clf.classify_chest_xray(image_path=img, generate_report=generate_report)
    return result


@app.post("/api/classify/brain")
async def classify_brain(
    image: UploadFile = File(...),
    generate_report: bool = Form(True),
):
    """Brain MRI / tumor specialized classification."""
    clf = get_classifier()
    img = _image_from_upload(image)
    result = clf.classify_brain_tumor(image_path=img, generate_report=generate_report)
    return result


@app.post("/api/classify/bone")
async def classify_bone(
    image: UploadFile = File(...),
    generate_report: bool = Form(True),
):
    """Bone X-ray / fracture specialized classification."""
    clf = get_classifier()
    img = _image_from_upload(image)
    result = clf.classify_bone_xray(image_path=img, generate_report=generate_report)
    return result


@app.post("/api/classify/text")
async def classify_text(req: TextReportRequest):
    """Text report only: extract diseases from report text."""
    clf = get_classifier()
    result = clf.classify_text_report(
        report_text=req.report_text,
        generate_report=False,
    )
    return result


@app.get("/api/health")
async def health():
    return {"status": "ok", "message": "Medical Classification API"}
