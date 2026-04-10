# 🧠 NeuroVision AI — College Presentation Master Guide

This document is your **complete end-to-end breakdown** of the entire NeuroVision AI platform. It is designed to give you everything you need to confidently stand in front of your college (HOD, Principal, Guides, and students) and explain exactly *what* you built, *how* you built it, and *why* it matters.

---

## 🌟 1. The Vision and Moto (The "Why")

**The Moto:** *"Where artificial intelligence meets the human side of healthcare."*

**The Vision:** We realized that modern healthcare relies heavily on siloed systems. If a patient lives in a rural area, getting a specialist radiologist to review an X-ray takes days. Mental health issues are heavily stigmatized and ignored because therapy is expensive. Doctor-patient booking flows are entirely disconnected from preliminary diagnostic data.

We wanted to build an **autonomous, full-stack hospital in the cloud**. A platform where a patient can walk in digitally, get an immediate AI assessment on a medical scan within 3 seconds, speak to a voice therapist about their anxiety, take cognitive tests, and instantly see a map of local specialists to book an appointment with their AI report already attached. We democratize access to clinical-grade intelligence.

---

## 🏗️ 2. System Architecture (The "How It Works")

We implemented an extremely modern, decoupled hybrid architecture optimized for speed and scalability:

*   **Frontend (The Face):** Built using **Next.js 15 (React App Router)** with Tailwind CSS and Radix UI. It provides an ultra-responsive, visually stunning "glassmorphism" dark-mode interface ensuring the patients feel they are using a premium, next-generation product.
*   **Backend (The Engine):** A highly concurrent **FastAPI (Python)** server. We chose FastAPI over Django/Flask because it handles asynchronous requests rapidly, keeping API wait times under 3 seconds even when processing heavy PyTorch/TensorFlow deep-learning models.
*   **The Database (The Memory):** We use **Supabase (PostgreSQL Cloud)**. It handles secure user authentication (JWT), sessions, and stores all appointment history and AI diagnostic findings securely.

**The Real-Time Data Flow:**
1. A patient uploads an X-ray on the Next.js UI (Port 3000).
2. The UI sends a REST API call to our FastAPI engine (Port 8000).
3. The engine dynamically routes the image to the correct PyTorch/Keras AI model.
4. The model computes the diagnosis probabilities.
5. Our system triggers the Groq LLaMA-3.3-70b large language model to instantly translate raw machine probabilities into a structured clinical radiologist's report.
6. The frontend renders the results with charts, auto-saves to Supabase, and allows the user to download a generated PDF using ReportLab!

---

## 🤖 3. The 5-Model AI Ensemble (The "Intelligence")

This is where the platform truly shines. Instead of pushing one generic AI model to classify everything poorly, we built a **5-model routing ensemble**. The backend parses what type of scan is uploaded and fires the dedicated specialist model.

### 🫁 1. CustomNet121 (Chest X-Ray Subsystem)
*   **Architecture:** A heavily fine-tuned, custom implementation of DenseNet121.
*   **Code Implementation:** Look at `finetune_chest_model.py` in our root folder. We built a custom script using TensorFlow/Keras to programmatically map 14 specific pathologies via the `ImageDataGenerator` and apply a custom Cosine Decay learning rate scheduler.
*   **Dataset used:** Formally trained on the massive **NIH ChestX-ray8 Dataset** consisting of 112,120 labeled images.
*   **Performance Tracking:** In our `chest_finetune_history.csv` log, you can see our exact real-world training progression over 10 epochs. The loss drops significantly down to **0.153**, capping the accuracy at a staggering **94.4%** across an 11-class categorization mapping.

### 🧠 2. InceptionV3 Ensemble (Neurology / Brain MRI)
*   **Architecture:** InceptionV3 with custom fully-connected classification heads.
*   **Code Implementation:** Demonstrated in our `braintTumor.ipynb` complete end-to-end training notebook which preprocesses the Kaggle image directories and maps the layers.
*   **Dataset used:** The **Brain Tumor MRI Dataset** consisting of 7,023 images.
*   **Performance:** Specifically targets 4 classes (Glioma, Meningioma, Pituitary tumor, and no tumor) achieving a phenomenal **98%+ accuracy**, effectively performing at clinical screening standards.

### 🦴 3. MedSigLIP (Orthopedics & Bone Scans)
*   **Architecture:** A cutting-edge HuggingFace Vision-Language Transformer.
*   **Approach:** By using image-text pairing, this model leverages **Zero-Shot Classification**, meaning we can throw practically any orthopedic variation at it and compare it against 20+ text pathology labels without explicitly fine-tuning for all 20 shapes.

### 📋 4. CheXpert DenseNet (Pathology Validation)
*   **Dataset used:** Stanford's CheXpert dataset (224,316 images).
*   **Function:** Works alongside CustomNet121 specifically to map 14 localized chest pathologies (like Edema vs Atelectasis) providing the probabilities seen on the diagnostic UI bars.

### ☁️ 5. Groq LLaMA-3.3-70b & MedGemma Fine-Tuning (Natural Language Engine)
*   **Inference Engine:** Instead of standard OpenAI API, we adopted the revolutionary LPU (Language Processing Unit) acceleration of **Groq**. This generates highly empathetic 1,500-token medical reports in less than two seconds.
*   **Custom NLP Fine-Tuning:** We also built an internal pipeline (`fine_tune_llm.py`) capable of fine-tuning `google/medgemma-27b-it` on specialized JSON medical datasets using Hugging Face AutoModelForCausalLM. This proves our architecture can operate entirely on local weight instances for specialized edge cases when internet API connectivity drops.

---

## 💎 4. Platform Modules and Features (The "Product")

NeuroVision AI is broken into **9 distinct modules** that cover the entire patient journey:

1.  **NeuroVision Diagnostics:** The core hub. Upload files, get the visual charts, generate the AI text report, and download the clinical PDF.
2.  **MedBot AI Chat:** A 24/7 symptom checker floating on the dashboard. It acts as an empathetic triage nurse.
3.  **Aria (Voice Therapist):** Utilizing the native Web Speech API and Groq responses, users suffering from anxiety can verbally speak into their microphones and have a humanistic mental-health grounding conversation without typing.
4.  **Mental Health Planner:** Automatically tests users with clinically recognized scales — **PHQ-9** for depression severity and **GAD-7** for anxiety. It outputs a score gauge and actionable weekly wellness plans.
5.  **Cognitive Games:** Tracks neurological baselines. Memory-pattern games mimicking the MMSE (Mini-Mental State Exam), speed tracking mimicking TMT (Trail Making Tests), and recall exercises.
6.  **Interactive Doctor Booking:** Uses React Leaflet mapping to display pin-drops of actual registered specialists. Users can filter by specialty, hit book, and choose online/offline modes while instantly attaching their prior AI diagnostic PDF limit.
7.  **Family Connect:** You can add up to 10 family members locally or invite them via UUID links, allowing caregivers to track their parents' diagnostic reports or mental health scores remotely.
8.  **Panchayat (VR Connect):** We embedded FrameVR native-WebVR to allow rural or isolated groups to enter a 3D virtual therapy or consultation room — supporting camera and mic.
9.  **Resource Hub:** Educational library covering cardiology to cognitive care mapping.

---

## 📈 5. How to Pitch This / The Talking Flow

If you are presenting this live, follow this narrative arc:

**Introduction (2 min):**
*"Good morning. Healthcare today is broken by borders, walls, and wait-times. Our team set out to build NeuroVision AI: to put the power of a full hospital inside a browser window using advanced artificial intelligence."*

**The AI Engine (3 min):**
*(Show the Diagnostics slide)* *"We did not just use an API. We custom-built a 5-model PyTorch and TensorFlow ensemble. We fine-tuned CustomNet121 on over 100,000 NIH images, achieving 94.4% accuracy. Our system dynamically routes an image—if it's a brain scan it hits our 98% accurate InceptionV3 model; if it's a bone scan, it triggers our zero-shot MedSigLIP transformer."*
*(Mention Groq)* *"But human beings don't want raw math probabilities. So we pass these tensor arrays into Groq's LLaMA 3.3 Large Language parameter model. In two seconds, it translates the math into a complete, radiologist-grade PDF clinic report."*

**The Platform Walkthrough (4 min):**
*(Show the Features UI)* *"We then wrapped this intelligence into a patient ecosystem. 
If someone is stressed about their diagnosis, they click on the Voice Therapist, Aria, and mentally decompress via a speaking interface without waiting weeks for a psychologist. 
If they need a real doctor, they open our live map, find a specialist, and book an appointment, automatically forwarding their AI findings directly to the doctor's portal."*

**Conclusion (1 min):**
*"NeuroVision AI effectively bridges deep-learning accuracy, real-time web infrastructure, and proactive mental health UX. Thank you."*

---

> **Important Tip for Defending Your Code:** If your professors ask how you actually trained the models and didn't just use an API, you point them directly to your raw code.
> - Open `finetune_chest_model.py` to prove your custom Early Stopping and manual Cosine Learning Rate Schedule functions.
> - Open `fine_tune_llm.py` to show you actually wrote the `MedicalLLMFineTuner` class that tokenizes and applies Data Collators for Language Modeling using PyTorch.
> - Open `chest_finetune_history.csv` to prove the exact accuracy numbers (94.3%) and loss (0.153) are backed up by your actual local execution logs over 10 epochs.
> - Open `braintTumor.ipynb` to show the raw visual outputs of the image preprocessing and InceptionV3 array structure directly from the Kaggle dataset.
