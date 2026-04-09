NeuroVision AI : A multimodal medical diagnostics.


![Synapse UI](https://github.com/SWAYAMPATEL30/MedAI/raw/main/synapse/public/dashboard-preview.png)

## 🚀 Key Features

- **NeuroVision Diagnostics**: Specialized AI models for Chest X-Rays, Bone Fractures, and Brain Tumors (MRI).
- **MedBot AI Chat**: A compassionate medical assistant powered by Groq (Llama 3.3).
- **Aria Voice Therapist**: Real-time voice interaction for mental health support.
- **Automated Clinical Reports**: Generates professional radiologist reports in PDF format using LLM-driven findings.
- **Supabase Integration**: Unified database for patient records, appointments, and diagnostic history.

## 🛠️ Tech Stack

- **Frontend**: Next.js 15, TypeScript, Tailwind CSS, Framer Motion, Lucide Icons.
- **Backend**: FastAPI (Python), Uvicorn.
- **AI Engine**: 
  - **Groq API**: Chat & Voice Logic (Llama 3.3).
  - **Google Gemini API**: Clinical Report Reasoning (1.5 Flash).
  - **Local Models**: TensorFlow/Keras (CustomNet121 for Chest, InceptionV3 for Brain).
- **Database**: Supabase (PostgreSQL) with RLS.

## 📦 Setup & Installation

### 1. Prerequisites
- Python 3.10+
- Node.js 18+
- Supabase Account

### 2. Backend Setup
1. Navigate to the root directory.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file and add your keys:
   ```env
   GROQ_API_KEY=your_groq_key
   GEMINI_API_KEY=your_gemini_key
   SUPABASE_URL=your_supabase_url
   SUPABASE_SERVICE_ROLE_KEY=your_service_key
   CONNECTION_STRING=your_postgres_connection_string
   ```
4. Start the backend:
   ```bash
   python api.py
   ```

### 3. Frontend Setup
1. Navigate to the `synapse/` directory.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Create a `.env.local` file:
   ```env
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
   ```
4. Start the development server:
   ```bash
   npm run dev
   ```

## 📄 License

This project is intended for research and educational purposes. Always consult a licensed medical professional for clinical diagnosis.

---
Created by **Swayam Patel**
