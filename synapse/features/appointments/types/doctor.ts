export interface TimeSlot {
  id: string;
  time: string;
  date: string;
  available: boolean;
}

export interface Review {
  id: string;
  patientName: string;
  rating: number;
  comment: string;
  date: string;
}

export interface Doctor {
  id: string;
  name: string;
  photo: string;
  specialization: string;
  degree: string;
  university: string;
  graduationYear: number;
  certifications: string[];
  bio: string;
  avgRating: number;
  reviewCount: number;
  city: string;
  area: string;
  clinicName: string;
  address: string;
  lat: number;
  lng: number;
  onlineAvailable: boolean;
  offlineAvailable: boolean;
  nextAvailable: string; // ISO date string
  availabilityColor: 'green' | 'yellow' | 'grey';
  reviews: Review[];
  timeSlots: TimeSlot[];
  consultationFee: number;
  experience: number; // years
}
