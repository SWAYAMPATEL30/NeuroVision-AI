<h1 align="center">
  <br>
  NeuroVision AI Platform
  <br>
</h1>

<h4 align="center">The Future of Primary Care is Intelligent.</h4>

<p align="center">
  <a href="#overview">Overview</a> •
  <a href="#key-features">Key Features</a> •
  <a href="#technical-architecture">Architecture</a> •
  <a href="#getting-started">Getting Started</a> •
  <a href="#ai-modules">AI Modules</a>
</p>

---

## Overview

**NeuroVision AI** is a production-ready, comprehensive digital health system designed to bridge the gap between advanced artificial intelligence and everyday primary care. Combining 24/7 intelligent virtual assistants, real-time clinical diagnostics (MRI/X-Ray analysis), and seamless telemedicine integration, NeuroVision AI brings world-class medicine to everyone's fingertips.

Previously a niche prototype, NeuroVision AI has evolved into a robust, high-performance platform capable of handling complete patient lifecycles — from initial symptom triaging using Large Language Models to clinical image verification by board-verified doctors.

## Key Features

- **NeuroVision AI Engine**: Instantly analyze Bone X-Rays, Brain MRIs, and Chest scans using cutting-edge deep learning models running on a FastAPI backend.
- **Intelligent MedBot (Aria)**: A 24/7 conversational Agent powered by Hugging Face Inference API (`zephyr-7b-beta`) customized with strict medical boundaries to provide safe, empathetic symptom checking.
- **Dynamic Telemedicine Booking**: Instantly filter specialists via Map or List view, and book In-Person visits, Video Consultations, or request asynchronous AI-report verifications without requiring a specific time slot.
- **Unified Medical Dashboard**: A newly redesigned Next.js 15 Glassmorphic dashboard that synchronizes appointments, stores downloaded radiology reports, and provides an at-a-glance system status.
- **Dyslexia-friendly Accessibility**: Built-in inclusive tools such as Dyslexia Font toggles to ensure maximum accessibility for all patients.
- **OneMedical-Inspired UX**: Premium, dark-mode first design system tailored to evoke trust and technological superiority.

## Technical Architecture

The platform operates on a modernized, decoupled architecture:

*   **Frontend (Client)**: Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS, Framer Motion, Leaflet (Map Integration), Lucide React.
*   **Backend (API)**: Python FastAPI, Uvicorn, PyTorch (Computer Vision / CLIP models).
*   **Database/Storage**: Supabase (configured with fallback mocking for local-only testing) & Browser LocalStorage for persistence.
*   **AI Integrations**: 
    *   Hugging Face API for LLM Inference.
    *   OpenAI (`gpt-4o-mini`) via AI SDK for structured medical reporting.

## Getting Started

To run the full platform locally, you will need to start both the Python backend and the Next.js frontend.

### 1. Backend Setup

Ensure you have Python 3.9+ installed.

```bash
cd NeuroVision AI/backend  # If applicable, or root
pip install -r requirements.txt
python api.py
```
*The FastAPI server will boot up on `http://localhost:8000`.*

### 2. Frontend Setup

Ensure you have Node.js 18+ installed.

```bash
cd NeuroVision AI
npm install
```

**Environment Variables**
Create a `.env.local` file in the `NeuroVision AI` directory with your required keys:
```env
NEXT_PUBLIC_HF_TOKEN=hf_your_token_here
OPENAI_API_KEY=sk-your_token_here

# Optional: For production database persistence (fallback mocked if empty)
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
```

**Run the app:**
```bash
npm run dev
```
*The application should now be live on `http://localhost:3000`.*

## AI Modules Deep Dive

### 1. NeuroVision
By leveraging PyTorch, the platform supports real-time inference on multiple model weights. Scans uploaded by patients are sent to the FastAPI service, where the image is processed and a clinical summary is generated in a downloadable report format using structured language generation.

### 2. Video Calling (WebRTC / Streams)
NeuroVision AI properly handles dynamic Next.js 15 route parameters (using `React.use()` for `params`) to ensure seamless transition from the Patient Dashboard directly into secure WebRTC Video Consultation sessions.

### 3. Voice IA & MedBot
The Chatbot uses LangChain-style prompts to enforce disclaimers ("I am an AI, not a substitute for a doctor") while safely analyzing the user's text. This ensures a human-like, instantaneous triage process.

---

> **Note**: For production deployment (Vercel/Render), ensure all Environment Variables from local are mirrored in the platform configuration. Database synchronization uses local state in development environments unless the Supabase keys are fully utilized.
