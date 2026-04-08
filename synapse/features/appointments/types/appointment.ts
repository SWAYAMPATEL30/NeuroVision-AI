export type AppointmentMode = 'verify' | 'online' | 'offline';
export type AppointmentStatus = 'pending' | 'confirmed' | 'cancelled' | 'completed';

export interface AttachedFile {
  name: string;
  type: 'xray' | 'report' | 'pdf';
  size?: number;
  url?: string;
}

export interface Appointment {
  id: string;
  doctorId: string;
  doctorName: string;
  doctorPhoto: string;
  doctorSpecialization: string;
  mode: AppointmentMode;
  status: AppointmentStatus;
  date?: string;
  time?: string;
  attachedFiles: AttachedFile[];
  aiReport?: string;
  scanType?: string;
  clinicAddress?: string;
  videoCallUrl?: string;
  createdAt: string;
  consentGiven: boolean;
}
