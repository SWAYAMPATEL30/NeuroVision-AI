import { Doctor } from '../types/doctor';

const today = new Date();
const tomorrow = new Date(today);
tomorrow.setDate(today.getDate() + 1);
const dayAfter = new Date(today);
dayAfter.setDate(today.getDate() + 2);
const nextWeek = new Date(today);
nextWeek.setDate(today.getDate() + 7);

function isoDate(d: Date) {
  return d.toISOString().split('T')[0];
}

function makeSlots(dateStr: string) {
  const times = ['09:00 AM', '10:00 AM', '11:00 AM', '02:00 PM', '03:00 PM', '04:00 PM'];
  return times.map((t, i) => ({
    id: `${dateStr}-${i}`,
    time: t,
    date: dateStr,
    available: i !== 2,
  }));
}

export const MOCK_DOCTORS: Doctor[] = [
  {
    id: 'd1',
    name: 'Dr. Ananya Sharma',
    photo: 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=200&h=200&fit=crop&crop=face',
    specialization: 'Radiologist',
    degree: 'MD Radiodiagnosis',
    university: 'AIIMS New Delhi',
    graduationYear: 2014,
    certifications: ['Board Certified Radiologist', 'FRCR (UK)', 'DNB Radiodiagnosis'],
    bio: 'Dr. Ananya Sharma is a senior radiologist with over 10 years of experience in diagnostic imaging. She specializes in chest and musculoskeletal radiology and has published 15+ peer-reviewed papers.',
    avgRating: 4.9,
    reviewCount: 214,
    city: 'Mumbai',
    area: 'Bandra West',
    clinicName: 'Clarity Imaging Center',
    address: '14, Hill Road, Bandra West, Mumbai - 400050',
    lat: 19.0596,
    lng: 72.8295,
    onlineAvailable: true,
    offlineAvailable: true,
    nextAvailable: isoDate(today),
    availabilityColor: 'green',
    consultationFee: 800,
    experience: 10,
    reviews: [
      { id: 'r1', patientName: 'Rahul M.', rating: 5, comment: 'Extremely thorough and explained every detail clearly.', date: '2025-03-10' },
      { id: 'r2', patientName: 'Sneha K.', rating: 5, comment: "Best radiologist I've consulted. Detected the issue other doctors missed.", date: '2025-02-22' },
      { id: 'r3', patientName: 'Priya N.', rating: 4, comment: 'Very professional and punctual.', date: '2025-01-15' },
    ],
    timeSlots: [...makeSlots(isoDate(today)), ...makeSlots(isoDate(tomorrow))],
  },
  {
    id: 'd2',
    name: 'Dr. Vikram Mehta',
    photo: 'https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=200&h=200&fit=crop&crop=face',
    specialization: 'Pulmonologist',
    degree: 'MD Pulmonary Medicine',
    university: 'KEM Hospital Mumbai',
    graduationYear: 2011,
    certifications: ['Fellowship in Pulmonary Medicine', 'FCCP (USA)', 'IDCCM'],
    bio: 'Dr. Vikram Mehta is a leading pulmonologist specializing in respiratory diseases, lung infections, and chest X-ray interpretation. He has 13+ years of clinical experience.',
    avgRating: 4.7,
    reviewCount: 187,
    city: 'Mumbai',
    area: 'Andheri East',
    clinicName: 'BreathRight Clinic',
    address: '5, Chakala Road, Andheri East, Mumbai - 400093',
    lat: 19.1136,
    lng: 72.8697,
    onlineAvailable: true,
    offlineAvailable: false,
    nextAvailable: isoDate(tomorrow),
    availabilityColor: 'yellow',
    consultationFee: 1200,
    experience: 13,
    reviews: [
      { id: 'r4', patientName: 'Amit S.', rating: 5, comment: 'Excellent diagnosis. My breathing issues resolved quickly.', date: '2025-03-05' },
      { id: 'r5', patientName: 'Kavya R.', rating: 4, comment: 'Good doctor, bit hard to get appointment.', date: '2025-02-10' },
    ],
    timeSlots: [...makeSlots(isoDate(tomorrow)), ...makeSlots(isoDate(dayAfter))],
  },
  {
    id: 'd3',
    name: 'Dr. Rajesh Nair',
    photo: 'https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=200&h=200&fit=crop&crop=face',
    specialization: 'Orthopedic Surgeon',
    degree: 'MS Orthopaedics',
    university: 'Kasturba Medical College, Manipal',
    graduationYear: 2009,
    certifications: ['DNB Orthopaedics', 'Fellowship in Joint Replacement (Germany)', 'ATLS Certified'],
    bio: 'Dr. Rajesh Nair is a highly skilled orthopedic surgeon specializing in fracture management, joint replacement, and sports medicine. He has performed 2000+ surgeries.',
    avgRating: 4.8,
    reviewCount: 312,
    city: 'Pune',
    area: 'Koregaon Park',
    clinicName: 'BoneHealth Orthopaedic Centre',
    address: '8, North Main Road, Koregaon Park, Pune - 411001',
    lat: 18.5362,
    lng: 73.8955,
    onlineAvailable: true,
    offlineAvailable: true,
    nextAvailable: isoDate(today),
    availabilityColor: 'green',
    consultationFee: 1500,
    experience: 15,
    reviews: [
      { id: 'r6', patientName: 'Suresh P.', rating: 5, comment: 'Brilliant surgeon! My fracture healed perfectly.', date: '2025-03-12' },
      { id: 'r7', patientName: 'Meera D.', rating: 5, comment: 'Very calm and reassuring. Excellent surgery outcome.', date: '2025-02-28' },
    ],
    timeSlots: [...makeSlots(isoDate(today)), ...makeSlots(isoDate(tomorrow))],
  },
  {
    id: 'd4',
    name: 'Dr. Priya Krishnamurthy',
    photo: 'https://images.unsplash.com/photo-1594824476967-48c8b964273f?w=200&h=200&fit=crop&crop=face',
    specialization: 'Neurologist',
    degree: 'DM Neurology',
    university: 'NIMHANS Bangalore',
    graduationYear: 2016,
    certifications: ['DM Neurology', 'Fellowship in Neuroradiology', 'Indian Academy of Neurology Member'],
    bio: 'Dr. Priya Krishnamurthy is an accomplished neurologist specializing in brain tumor diagnosis and neuroimaging interpretation. She is a faculty member at a leading medical college.',
    avgRating: 4.6,
    reviewCount: 143,
    city: 'Bangalore',
    area: 'Indiranagar',
    clinicName: 'NeuroPath Brain and Spine Centre',
    address: '22, 100 Feet Road, Indiranagar, Bangalore - 560038',
    lat: 12.9784,
    lng: 77.6408,
    onlineAvailable: true,
    offlineAvailable: true,
    nextAvailable: isoDate(dayAfter),
    availabilityColor: 'yellow',
    consultationFee: 1800,
    experience: 8,
    reviews: [
      { id: 'r8', patientName: 'Arjun T.', rating: 5, comment: 'Very detailed consultation and prompt diagnosis.', date: '2025-03-01' },
      { id: 'r9', patientName: 'Lakshmi V.', rating: 4, comment: 'Good doctor, explained MRI results clearly.', date: '2025-01-20' },
    ],
    timeSlots: [...makeSlots(isoDate(dayAfter)), ...makeSlots(isoDate(nextWeek))],
  },
  {
    id: 'd5',
    name: 'Dr. Arun Gupta',
    photo: 'https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=200&h=200&fit=crop&crop=face',
    specialization: 'Radiologist',
    degree: 'MD Radiology',
    university: 'Grant Medical College, Mumbai',
    graduationYear: 2010,
    certifications: ['DNB Radiology', 'Interventional Radiology Fellowship', 'FRCR (London)'],
    bio: 'Dr. Arun Gupta has extensive experience in diagnostic and interventional radiology. He specializes in bone density studies and X-ray interpretation for trauma cases.',
    avgRating: 4.5,
    reviewCount: 98,
    city: 'Pune',
    area: 'Aundh',
    clinicName: 'PrecisionScan Radiology',
    address: '3, ITI Road, Aundh, Pune - 411007',
    lat: 18.5579,
    lng: 73.8087,
    onlineAvailable: false,
    offlineAvailable: true,
    nextAvailable: isoDate(nextWeek),
    availabilityColor: 'grey',
    consultationFee: 700,
    experience: 14,
    reviews: [
      { id: 'r10', patientName: 'Ganesh M.', rating: 4, comment: 'Good radiology expert. Reports are very detailed.', date: '2025-02-05' },
    ],
    timeSlots: makeSlots(isoDate(nextWeek)),
  },
  {
    id: 'd6',
    name: 'Dr. Sunita Verma',
    photo: 'https://images.unsplash.com/photo-1527613426441-4da17471b66d?w=200&h=200&fit=crop&crop=face',
    specialization: 'Pulmonologist',
    degree: 'MD Respiratory Medicine',
    university: 'PGIMER Chandigarh',
    graduationYear: 2013,
    certifications: ['FCCP', 'IDCCM', 'Sleep Medicine Certification'],
    bio: 'Dr. Sunita Verma is a renowned pulmonologist in Bangalore with expertise in COPD, asthma, and chest infections. She has successfully treated 5000+ patients.',
    avgRating: 4.8,
    reviewCount: 267,
    city: 'Bangalore',
    area: 'Jayanagar',
    clinicName: 'LungCare Specialist Clinic',
    address: '15, 4th Block, Jayanagar, Bangalore - 560041',
    lat: 12.9306,
    lng: 77.5833,
    onlineAvailable: true,
    offlineAvailable: true,
    nextAvailable: isoDate(today),
    availabilityColor: 'green',
    consultationFee: 900,
    experience: 11,
    reviews: [
      { id: 'r11', patientName: 'Chitra B.', rating: 5, comment: 'Best pulmonologist in Bangalore! Diagnosed my asthma correctly.', date: '2025-03-15' },
      { id: 'r12', patientName: 'Ravi K.', rating: 5, comment: 'Very empathetic and knowledgeable doctor.', date: '2025-03-02' },
    ],
    timeSlots: [...makeSlots(isoDate(today)), ...makeSlots(isoDate(tomorrow))],
  },
];

import { supabase } from '@/lib/supabaseClient';

export async function fetchDoctors(): Promise<Doctor[]> {
  try {
    const { data, error } = await supabase.from('doctors').select('*');
    if (error) {
      console.warn('Supabase fetch failed or not configured, using mocks', error);
      return MOCK_DOCTORS;
    }
    if (data && data.length > 0) {
      // Map supabase data to our doctor type
      const supabaseDoctors = data.map(d => ({
        id: d.id,
        name: d.name || 'Unknown',
        photo: d.photo || 'https://via.placeholder.com/150',
        specialization: d.specialization || d.specialty || 'General',
        degree: d.degree || 'MD',
        university: d.university || '',
        graduationYear: d.graduationYear || 2020,
        certifications: d.certifications || [],
        bio: d.bio || '',
        avgRating: d.avgRating || 5.0,
        reviewCount: d.reviewCount || 0,
        city: d.city || 'Unknown',
        area: d.area || '',
        clinicName: d.clinicName || d.clinic || '',
        address: d.clinicAddress || d.address || '',
        lat: d.lat || 0,
        lng: d.lng || 0,
        onlineAvailable: d.onlineAvailable ?? d.consultLine ?? true,
        offlineAvailable: d.offlineAvailable ?? d.consultClinic ?? true,
        nextAvailable: d.nextAvailable || isoDate(today),
        availabilityColor: d.availabilityColor || 'green',
        consultationFee: d.consultationFee || 500,
        experience: d.experience || 0,
        reviews: [],
        timeSlots: [...makeSlots(isoDate(today)), ...makeSlots(isoDate(tomorrow))],
      }));
      return [...supabaseDoctors, ...MOCK_DOCTORS];
    }
  } catch (err) {
    console.error(err);
  }
  return MOCK_DOCTORS;
}

export async function fetchDoctorById(id: string): Promise<Doctor | undefined> {
  const allDoctors = await fetchDoctors();
  return allDoctors.find(d => d.id === id);
}
