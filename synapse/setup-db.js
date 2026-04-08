const { Client } = require('pg');

const connectionString = "postgresql://postgres:Pass%40123Sept%248794@db.qakpizqrjljtnqlaaber.supabase.co:5432/postgres";

const sql = `
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

INSERT INTO public.doctors ("id", "name", "specialization", "city", "consultationFee", "experience", "availabilityColor", "nextAvailable")
VALUES 
('d1', 'Dr. Ananya Sharma', 'Radiologist', 'Mumbai', 800, 10, 'green', '2025-04-08'),
('d2', 'Dr. Vikram Mehta', 'Pulmonologist', 'Mumbai', 1200, 13, 'yellow', '2025-04-09'),
('d3', 'Dr. Rajesh Nair', 'Orthopedic Surgeon', 'Pune', 1500, 15, 'green', '2025-04-08'),
('d4', 'Dr. Priya Krishnamurthy', 'Neurologist', 'Bangalore', 1800, 8, 'yellow', '2025-04-10'),
('d5', 'Dr. Arun Gupta', 'Radiologist', 'Pune', 700, 14, 'grey', '2025-04-15')
ON CONFLICT ("id") DO NOTHING;
`;

async function setup() {
  const client = new Client({ connectionString });
  try {
    console.log("Connecting...");
    await client.connect();
    console.log("Connected. Running SQL...");
    await client.query(sql);
    console.log("SUCCESS! Production tables created.");
  } catch (err) {
    console.error("FAILED:", err);
  } finally {
    await client.end();
  }
}

setup();
