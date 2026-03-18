# V0 Prompt for Medical Disease Classification Website

**Copy the entire prompt below into [v0.dev](https://v0.dev) to generate a working frontend. Then use the API section at the bottom to build a FastAPI backend that your `medical_classifier.py` can serve.**

---

## PROMPT TO PASTE IN V0

```
Build a modern, professional medical AI diagnosis assistant web app with Next.js 14 (App Router), React, and Tailwind CSS. The app will connect to a Python backend API for medical image and report analysis.

### CORE FEATURES

1. **Landing / Home Page**
   - Hero section: "Medical Disease Classification System" – AI-powered analysis of X-rays, CT scans, MRIs, and medical reports
   - Subtitle: Multi-model AI (MedSigLIP, CheXpert, CXR Foundation, MedGemma) for accurate disease detection
   - Clear CTA: "Upload Image" or "Analyze Report" – scroll to upload section or open modal
   - Trust badges: "Chest X-Ray • Brain MRI • Bone X-Ray • Text Reports"
   - Clean, clinical aesthetic: soft blues/teals, plenty of whitespace, minimal clutter. Use a font like Inter or DM Sans. Avoid generic "AI slop" – aim for a calm, hospital/healthtech feel.

2. **Upload & Analysis Section** (main workflow)
   - **Modality selector**: Tabs or dropdown – "General (Any Image)", "Chest X-Ray", "Brain MRI", "Bone X-Ray", "Text Report Only"
   - **Image upload** (for image modes): Drag-and-drop zone + file picker. Accept PNG, JPG, JPEG. Show image preview and filename. Optional: patient fields (Name, Patient ID, Age, Gender) – can be collapsible "Add patient info".
   - **Text input** (for "Text Report Only"): Large textarea for pasting radiology/clinical report text. Button: "Analyze Report".
   - **Analyze button**: "Analyze" / "Run Analysis". On click, send request to backend API (see API spec below). Show loading state (spinner/skeleton) with message like "Running AI models... This may take 30–60 seconds."
   - Use `fetch` to `POST` to configurable `NEXT_PUBLIC_API_URL` (e.g. `http://localhost:8000`) with the appropriate endpoint per modality.

3. **Results Page / Section**
   - After successful analysis, show:
     - **Best prediction**: Large card – "Primary Finding: [disease name]" and "Confidence: XX%"
     - **Model used**: e.g. "MedSigLIP" / "CheXpert" / "MedGemma-27b-it"
     - **Detailed predictions** (expandable): List of top diseases with confidence bars or percentages (from `classifications` in API response)
     - **Generated report**: Scrollable text area or styled div showing the radiology report (Markdown-friendly if backend sends it)
     - **Actions**: "Download Report (TXT)", "Download Report (PDF)" – buttons that call backend endpoints like `GET /api/report?format=txt|pdf` or similar, or use report text for client-side download
   - If **text-only** analysis: show "Extracted diseases" list (disease name + category) instead of image-based predictions.
   - **Error handling**: If API returns error or 4xx/5xx, show clear message: "Analysis failed. Please try again or check the backend."

4. **Navigation & Layout**
   - Sticky header: Logo/app name "MedAI Classifier", nav links: Home, Analyze, About. Optional: Login / Register (simple modals or separate routes – can be placeholder for now).
   - Footer: Disclaimer – "For research/education. Not a substitute for professional medical advice." Plus links to About, Privacy, Contact if you add those routes.

5. **About Page**
   - Short description of the system: multiple AI models (MedSigLIP, CheXpert, CXR Foundation, MedGemma, custom brain/chest models), support for chest X-rays, brain MRIs, bone X-rays, and text reports.
   - List supported modalities and output (predictions, confidence, radiology report). Keep it concise and professional.

### TECHNICAL REQUIREMENTS

- Use **Next.js 14** with App Router. Use **React Server Components** where it makes sense; keep client interactivity (forms, upload, fetch) in **"use client"** components.
- Use **Tailwind CSS** for all styling. No random CSS-in-JS unless it’s minimal.
- **Environment variable**: `NEXT_PUBLIC_API_URL` for the backend base URL (e.g. `http://localhost:8000`). Use it in all `fetch` calls.
- **State**: Keep upload state, analysis results, and loading/error in React state (useState). Optional: use a small context for "last result" if you have multiple pages.
- **Responsive**: Mobile-first. Upload zone, results cards, and nav should work on small screens.

### API CONTRACT (Backend to implement)

Base URL: `NEXT_PUBLIC_API_URL` (e.g. `http://localhost:8000`).

- **POST /api/classify**  
  - Body: `multipart/form-data` – `image` (file), optional `report_text` (string), optional `generate_report` (boolean).  
  - Use for "General (Any Image)" mode.

- **POST /api/classify/chest**  
  - Body: `multipart/form-data` – `image` (file), optional `generate_report` (boolean).  
  - Use for "Chest X-Ray" mode.

- **POST /api/classify/brain**  
  - Body: `multipart/form-data` – `image` (file), optional `generate_report` (boolean).  
  - Use for "Brain MRI" mode.

- **POST /api/classify/bone**  
  - Body: `multipart/form-data` – `image` (file), optional `generate_report` (boolean).  
  - Use for "Bone X-Ray" mode.

- **POST /api/classify/text**  
  - Body: `application/json` – `{ "report_text": "..." }`.  
  - Use for "Text Report Only" mode.

**Response** (all classify endpoints): JSON like:

```json
{
  "input_type": "image" | "chest_xray" | "brain_tumor" | "bone_xray" | "text",
  "classifications": { "medsiglip": {...}, "chexpert": {...}, "cxr": {...} },
  "best_prediction": { "model": "...", "disease": "...", "confidence": 0.95 },
  "report": "Full radiology report text...",
  "extracted_diseases": { "diseases": [...], "total_found": 3 }
}
```

Optional: **GET /api/report/pdf** and **GET /api/report/txt** with `?id=<session_or_request_id>` if you store reports server-side; otherwise, use the `report` string from the classify response for client-side download.

### UI NOTES

- Use subtle shadows, rounded corners (e.g. `rounded-xl`), and a restrained color palette (e.g. blue-50/100/600, slate for text).
- Icons: use Lucide React or Heroicons for upload, report, check, alert.
- Ensure sufficient contrast and focus states for accessibility.
```

---

## Next Steps: Linking with Your Backend

A ready-to-use FastAPI backend is in **`api.py`** in this project. It wraps `MedicalClassifier` and exposes the endpoints above.

1. **Install API deps**:  
   `pip install -r requirements.txt && pip install -r requirements_api.txt`

2. **Run the API**:  
   `uvicorn api:app --reload --port 8000`  
   (from the project root where `api.py` and `medical_classifier.py` live)

3. **CORS**: Already enabled in `api.py` for `localhost:3000` and `*.vercel.app`.

4. **Env**: In your V0/Next.js app, set `NEXT_PUBLIC_API_URL=http://localhost:8000` (or your deployed API URL).

5. **Run frontend**: `npm run dev` in the V0 app. Use "Analyze" in the UI to call the backend.

---

## Quick Reference: MedicalClassifier Methods

| Frontend mode    | Backend method                |
|------------------|-------------------------------|
| General          | `classifier.classify(image_path=..., report_text=..., generate_report=...)` |
| Chest X-Ray      | `classifier.classify_chest_xray(image_path=..., generate_report=...)`      |
| Brain MRI        | `classifier.classify_brain_tumor(image_path=..., generate_report=...)`     |
| Bone X-Ray       | `classifier.classify_bone_xray(image_path=..., generate_report=...)`       |
| Text Report Only | `classifier.classify_text_report(report_text=...)` |

Use this table when implementing your FastAPI routes.
