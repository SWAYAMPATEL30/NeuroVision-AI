import psycopg2
import sys

conn_str = "postgresql://postgres.qakpizqrjljtnqlaaber:Pass%40123Sept%248794@aws-0-ap-south-1.pooler.supabase.com:5432/postgres"

sql = """
-- 1. Create the Doctors table
CREATE TABLE IF NOT EXISTS public.doctors (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    photo TEXT,
    specialization TEXT,
    degree TEXT,
    university TEXT,
    graduation_year INT,
    certifications TEXT[], 
    bio TEXT,
    avg_rating DECIMAL DEFAULT 5.0,
    review_count INT DEFAULT 0,
    city TEXT,
    area TEXT,
    clinic_name TEXT,
    address TEXT,
    lat DECIMAL,
    lng DECIMAL,
    online_available BOOLEAN DEFAULT TRUE,
    offline_available BOOLEAN DEFAULT TRUE,
    next_available TEXT,
    availability_color TEXT,
    consultation_fee INT,
    experience INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Create the Appointments table
CREATE TABLE IF NOT EXISTS public.appointments (
    id TEXT PRIMARY KEY,
    doctor_id TEXT REFERENCES public.doctors(id),
    doctor_name TEXT,
    doctor_photo TEXT,
    doctor_specialization TEXT,
    mode TEXT CHECK (mode IN ('online', 'offline', 'verify')),
    status TEXT DEFAULT 'confirmed',
    date TEXT,
    time TEXT,
    attached_files JSONB DEFAULT '[]',
    ai_report TEXT,
    scan_type TEXT,
    clinic_address TEXT,
    video_call_url TEXT,
    patient_name TEXT,
    patient_phone TEXT,
    consent_given BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Enable RLS
ALTER TABLE public.doctors ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.appointments ENABLE ROW LEVEL SECURITY;

-- 4. Create Public Access Policies
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Enable all access for doctors') THEN
        CREATE POLICY "Enable all access for doctors" ON public.doctors FOR ALL USING (true);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Enable all access for appointments') THEN
        CREATE POLICY "Enable all access for appointments" ON public.appointments FOR ALL USING (true);
    END IF;
END $$;

-- 5. Seed Dummy Doctors
INSERT INTO public.doctors (id, name, specialization, city, consultation_fee, experience, availability_color, next_available)
VALUES 
('d1', 'Dr. Ananya Sharma', 'Radiologist', 'Mumbai', 800, 10, 'green', '2025-04-10'),
('d2', 'Dr. Vikram Mehta', 'Pulmonologist', 'Mumbai', 1200, 13, 'yellow', '2025-04-11'),
('d3', 'Dr. Rajesh Nair', 'Orthopedic Surgeon', 'Pune', 1500, 15, 'green', '2025-04-10'),
('d4', 'Dr. Priya Krishnamurthy', 'Neurologist', 'Bangalore', 1800, 8, 'yellow', '2025-04-12'),
('d5', 'Dr. Arun Gupta', 'Radiologist', 'Pune', 700, 14, 'grey', '2025-04-17'),
('d6', 'Dr. Sunita Verma', 'Pulmonologist', 'Bangalore', 900, 11, 'green', '2025-04-10')
ON CONFLICT (id) DO NOTHING;
"""

try:
    print("Connecting to Supabase...")
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()
    print("Running SQL script...")
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()
    print("Success! Tables created and seeded.")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
