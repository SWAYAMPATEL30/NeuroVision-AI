import psycopg2
import sys
import socket

# User's provided connection string
password_plain = "Pass@123Sept$8794"
password_encoded = "Pass%40123Sept%248794"
project_ref = "qakpizqrjljtnqlaaber"

# Try different ways to connect
def try_connect(host, user, password, dbname="postgres", port="5432"):
    try:
        print(f"Testing connection to {host}...")
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port,
            connect_timeout=10
        )
        return conn
    except Exception as e:
        print(f"Failed to connect to {host}: {e}")
        return None

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
('d5', 'Dr. Arun Gupta', 'Radiologist', 'Pune', 700, 14, 'grey', '2025-04-15')
ON CONFLICT ("id") DO NOTHING;
"""

# Try the hosts
hosts = [
    f"db.{project_ref}.supabase.co",
    f"aws-0-ap-south-1.pooler.supabase.com" # Common for India region
]

conn = None
for h in hosts:
    # Handle user format for pooler
    user = f"postgres.{project_ref}" if "pooler" in h else "postgres"
    conn = try_connect(h, user, password_plain)
    if conn: break

if not conn:
    print("Could not connect to any host. Trying IPv6 manually...")
    # Last ditch attempt with the IPv6 NSLOOKUP gave us
    try:
        conn = psycopg2.connect(
            host="2406:da12:b78:de15:787e:5eb7:2bf0:4700",
            dbname="postgres",
            user="postgres",
            password=password_plain,
            port="5432",
            connect_timeout=10
        )
    except:
        pass

if conn:
    try:
        cur = conn.cursor()
        print("Executing SQL...")
        cur.execute(sql)
        conn.commit()
        print("SUCCESS! Tables created and seeded correctly.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"SQL Error: {e}")
else:
    print("FATAL: All connection attempts failed. Please ensure your database is active and accepting connections.")
