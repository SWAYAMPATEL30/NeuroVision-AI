import { supabase } from '@/lib/supabaseClient';
import { Appointment, AppointmentMode, AttachedFile } from '../types/appointment';
import { Doctor, TimeSlot } from '../types/doctor';

export async function bookAppointment(
  doctor: Doctor,
  mode: AppointmentMode,
  slot: TimeSlot | null,
  attachedFiles: AttachedFile[],
  aiReport: string,
  scanType: string,
  consentGiven: boolean,
  patientName: string = "Unknown",
  patientPhone: string = ""
): Promise<Appointment> {
  const appointment: Partial<Appointment> & { patientName: string, patientPhone: string } = {
    id: `appt-${Date.now()}`,
    doctorId: doctor.id,
    doctorName: doctor.name,
    doctorPhoto: doctor.photo,
    doctorSpecialization: doctor.specialization,
    mode,
    status: 'confirmed',
    date: slot?.date || new Date().toISOString().split('T')[0],
    time: slot?.time || "09:00 AM",
    attachedFiles,
    aiReport,
    scanType,
    clinicAddress: doctor.address,
    videoCallUrl: mode === 'online' ? `https://meet.neurovision.ai/room/${Date.now()}` : undefined,
    createdAt: new Date().toISOString(),
    consentGiven,
    patientName,
    patientPhone
  };

  const { data, error } = await supabase
    .from('appointments')
    .insert([appointment])
    .select()
    .single();

  if (error) {
    console.error('Supabase booking failed:', error);
    // Fallback to localStorage for demo if DB is not ready
    if (typeof window !== 'undefined') {
      const existing = JSON.parse(localStorage.getItem('neurovision_appointments') || '[]');
      existing.push(appointment);
      localStorage.setItem('neurovision_appointments', JSON.stringify(existing));
    }
    return appointment as Appointment;
  }

  return data as Appointment;
}

export async function getDoctorAppointments(doctorId: string): Promise<Appointment[]> {
  const { data, error } = await supabase
    .from('appointments')
    .select('*')
    .eq('doctorId', doctorId)
    .order('createdAt', { ascending: false });

  if (error) {
    console.error('Error fetching doctor appointments:', error);
    return [];
  }
  return data || [];
}

export function getStoredAppointments(): Appointment[] {
  if (typeof window === 'undefined') return [];
  return JSON.parse(localStorage.getItem('neurovision_appointments') || '[]');
}

export async function cancelAppointment(id: string): Promise<void> {
  const { error } = await supabase
    .from('appointments')
    .update({ status: 'cancelled' })
    .eq('id', id);
  
  if (error) {
    console.error('Error cancelling appointment:', error);
    // Fallback
    if (typeof window !== 'undefined') {
      const existing: Appointment[] = JSON.parse(localStorage.getItem('neurovision_appointments') || '[]');
      const updated = existing.map(a => a.id === id ? { ...a, status: 'cancelled' as const } : a);
      localStorage.setItem('neurovision_appointments', JSON.stringify(updated));
    }
  }
}
