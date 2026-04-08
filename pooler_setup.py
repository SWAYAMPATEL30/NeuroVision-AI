import psycopg2
import sys

# Try the Session Bouncer (Port 6543)
conn_str = "postgresql://postgres.qakpizqrjljtnqlaaber:Pass%40123Sept%248794@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"

sql = """
-- Create tables
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

CREATE TABLE IF NOT EXISTS public.appointments (
    "id" TEXT PRIMARY KEY,
    "doctorId" TEXT REFERENCES public.doctors("id"),
    "doctorName" TEXT,
    "doctorPhoto" TEXT,
    "doctorSpecialization" TEXT,
    "mode" TEXT,
    "status" TEXT DEFAULT 'confirmed',
    "date" TEXT,
    "time" TEXT,
    "attachedFiles" JSONB DEFAULT '[]',
    "aiReport" TEXT,
    "scanType" TEXT,
    "clinicAddress" TEXT,
    "videoCallUrl" TEXT,
    "patientName" TEXT,
    "patientPhone" TEXT,
    "consentGiven" BOOLEAN DEFAULT TRUE,
    "createdAt" TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.doctors ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.appointments ENABLE ROW LEVEL SECURITY;

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Public Read Doctors') THEN
        CREATE POLICY "Public Read Doctors" ON public.doctors FOR SELECT USING (true);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Public All Appointments') THEN
        CREATE POLICY "Public All Appointments" ON public.appointments FOR ALL USING (true);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Public All Doctors') THEN
        CREATE POLICY "Public All Doctors" ON public.doctors FOR ALL USING (true);
    END IF;
END $$;

INSERT INTO public.doctors ("id", "name", "specialization", "city", "consultationFee", "experience", "availabilityColor", "nextAvailable")
VALUES 
('d1', 'Dr. Ananya Sharma', 'Radiologist', 'Mumbai', 800, 10, 'green', '2025-04-08'),
('d2', 'Dr. Vikram Mehta', 'Pulmonologist', 'Mumbai', 1200, 13, 'yellow', '2025-04-09'),
('d3', 'Dr. Rajesh Nair', 'Orthopedic Surgeon', 'Pune', 1500, 15, 'green', '2025-04-08'),
('d4', 'Dr. Priya Krishnamurthy', 'Neurologist', 'Bangalore', 1800, 8, 'yellow', '2025-04-10'),
('d5', 'Dr. Arun Gupta', 'Radiologist', 'Pune', 700, 14, 'grey', '2025-04-15'),
('d6', 'Dr. Sunita Verma', 'Pulmonologist', 'Bangalore', 900, 11, 'green', '2025-04-08')
ON CONFLICT ("id") DO NOTHING;
"""

try:
    print(f"Connecting to Pooler on port 6543...")
    conn = psycopg2.connect(conn_str, connect_timeout=15)
    cur = conn.cursor()
    print("Executing SQL...")
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()
    print("SUCCESS! Tables created via Pooler.")
except Exception as e:
    print(f"Pooler 6543 Failed: {e}")
    # Try port 5432 with bouncer user format as backup
    try:
        print("Trying port 5432 with pooler user format...")
        conn_str_alt = "postgresql://postgres.qakpizqrjljtnqlaaber:Pass%40123Sept%248794@aws-0-ap-south-1.pooler.supabase.com:5432/postgres"
        conn = psycopg2.connect(conn_str_alt, connect_timeout=15)
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
        print("SUCCESS! Tables created via Pooler (5432).")
    except Exception as e2:
         print(f"Alt Pooler Failed: {e2}")
         sys.exit(1)
