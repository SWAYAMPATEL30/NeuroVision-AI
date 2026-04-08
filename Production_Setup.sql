-- ==========================================
-- SYNAPSE AI PRODUCTION DATABASE SCHEMA
-- ==========================================

-- 1. DOCTORS TABLE
-- Storage for verified medical professionals
CREATE TABLE IF NOT EXISTS public.doctors (
    "id" TEXT PRIMARY KEY,
    "name" TEXT NOT NULL,
    "photo" TEXT,
    "specialization" TEXT,
    "degree" TEXT,
    "university" TEXT,
    "graduationYear" INT,
    "certifications" TEXT[], 
    "bio" TEXT,
    "avgRating" DECIMAL DEFAULT 5.0,
    "reviewCount" INT DEFAULT 0,
    "city" TEXT,
    "area" TEXT,
    "clinicName" TEXT,
    "address" TEXT,
    "lat" DECIMAL,
    "lng" DECIMAL,
    "onlineAvailable" BOOLEAN DEFAULT TRUE,
    "offlineAvailable" BOOLEAN DEFAULT TRUE,
    "nextAvailable" TEXT,
    "availabilityColor" TEXT,
    "consultationFee" INT,
    "experience" INT,
    "createdAt" TIMESTAMPTZ DEFAULT NOW()
);

-- 2. APPOINTMENTS TABLE
-- Real-time booking and status management
CREATE TABLE IF NOT EXISTS public.appointments (
    "id" TEXT PRIMARY KEY,
    "doctorId" TEXT REFERENCES public.doctors("id") ON DELETE CASCADE,
    "doctorName" TEXT,
    "doctorPhoto" TEXT,
    "doctorSpecialization" TEXT,
    "mode" TEXT CHECK ("mode" IN ('online', 'offline', 'verify')),
    "status" TEXT DEFAULT 'confirmed' CHECK ("status" IN ('confirmed', 'pending', 'cancelled', 'completed')),
    "date" TEXT NOT NULL,
    "time" TEXT NOT NULL,
    "attachedFiles" JSONB DEFAULT '[]',
    "aiReport" TEXT,
    "scanType" TEXT,
    "clinicAddress" TEXT,
    "videoCallUrl" TEXT,
    "patientName" TEXT NOT NULL,
    "patientPhone" TEXT,
    "consentGiven" BOOLEAN DEFAULT TRUE,
    "createdAt" TIMESTAMPTZ DEFAULT NOW()
);

-- 3. PATIENT RECORDS (Production Table)
-- Persistence for patient medical history and profile
CREATE TABLE IF NOT EXISTS public.patients (
    "id" TEXT PRIMARY KEY,
    "name" TEXT NOT NULL,
    "email" TEXT UNIQUE,
    "age" INT,
    "gender" TEXT,
    "bloodGroup" TEXT,
    "emergencyContact" TEXT,
    "createdAt" TIMESTAMPTZ DEFAULT NOW()
);

-- 4. DIAGNOSTIC REPORTS
-- Storage for all AI scans independent of bookings
CREATE TABLE IF NOT EXISTS public.diagnostic_reports (
    "id" TEXT PRIMARY KEY,
    "patientName" TEXT,
    "patientAge" TEXT,
    "patientGender" TEXT,
    "scanType" TEXT,
    "disease" TEXT,
    "confidence" DECIMAL,
    "reportText" TEXT,
    "classifications" JSONB DEFAULT '{}',
    "imageUrl" TEXT,
    "createdAt" TIMESTAMPTZ DEFAULT NOW()
);

-- 5. SECURITY & REAL-TIME
-- Enable RLS and Real-time subscriptions
ALTER TABLE public.doctors ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.diagnostic_reports ENABLE ROW LEVEL SECURITY;

-- 6. ACCESS POLICIES (Production Ready)
-- Enable public access for demo purposes, restricted in real production
DO $$ 
BEGIN
    -- Doctors
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Public Read Doctors') THEN
        CREATE POLICY "Public Read Doctors" ON public.doctors FOR SELECT USING (true);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Public All Access Doctors') THEN
        CREATE POLICY "Public All Access Doctors" ON public.doctors FOR ALL USING (true);
    END IF;

    -- Appointments
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Public All Access Appointments') THEN
        CREATE POLICY "Public All Access Appointments" ON public.appointments FOR ALL USING (true);
    END IF;

    -- Diagnostic Reports
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Public All Access Reports') THEN
        CREATE POLICY "Public All Access Reports" ON public.diagnostic_reports FOR ALL USING (true);
    END IF;
END $$;

-- 6. SEED DATA
-- Injecting the required dummy doctors for Synapse verification
INSERT INTO public.doctors ("id", "name", "specialization", "city", "consultationFee", "experience", "availabilityColor", "nextAvailable")
VALUES 
('d1', 'Dr. Ananya Sharma', 'Radiologist', 'Mumbai', 800, 10, 'green', '2025-04-08'),
('d2', 'Dr. Vikram Mehta', 'Pulmonologist', 'Mumbai', 1200, 13, 'yellow', '2025-04-09'),
('d3', 'Dr. Rajesh Nair', 'Orthopedic Surgeon', 'Pune', 1500, 15, 'green', '2025-04-08'),
('d4', 'Dr. Priya Krishnamurthy', 'Neurologist', 'Bangalore', 1800, 8, 'yellow', '2025-04-10'),
('d5', 'Dr. Arun Gupta', 'Radiologist', 'Pune', 700, 14, 'grey', '2025-04-15')
ON CONFLICT ("id") DO NOTHING;
