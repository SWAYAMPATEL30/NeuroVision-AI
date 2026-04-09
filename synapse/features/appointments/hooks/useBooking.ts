"use client";
import { useState, useCallback, useMemo } from 'react';
import { Doctor, TimeSlot } from '../types/doctor';
import { Appointment, AppointmentMode, AttachedFile } from '../types/appointment';
import { bookAppointment } from '../services/bookingApi';

type BookingStep = 'select-mode' | 'select-doctor' | 'doctor-profile' | 'select-slot' | 'consent' | 'confirming' | 'confirmed';

export function useBooking(
  aiReport: string,
  scanType: string,
  uploadedFileName: string,
  patientName: string
) {
  const [step, setStep] = useState<BookingStep>('select-mode');
  const [mode, setMode] = useState<AppointmentMode | null>(null);
  const [selectedDoctor, setSelectedDoctor] = useState<Doctor | null>(null);
  const [selectedSlot, setSelectedSlot] = useState<TimeSlot | null>(null);
  const [consentGiven, setConsentGiven] = useState(false);
  const [appointment, setAppointment] = useState<Appointment | null>(null);
  const [error, setError] = useState<string | null>(null);

  const attachedFiles: AttachedFile[] = useMemo(() => {
    const files: AttachedFile[] = [
      { name: 'AI Diagnostic Report.pdf', type: 'report' }
    ];
    if (uploadedFileName) {
      files.push({ name: uploadedFileName, type: 'xray' });
    }
    return files;
  }, [uploadedFileName]);

  const selectMode = useCallback((m: AppointmentMode) => {
    setMode(m);
    setStep('select-doctor');
  }, []);

  const selectDoctor = useCallback((d: Doctor) => {
    setSelectedDoctor(d);
    setStep('doctor-profile');
  }, []);

  const proceedToSlot = useCallback(() => {
    if (mode === 'verify') {
      setStep('consent');
    } else {
      setStep('select-slot');
    }
  }, [mode]);

  const selectSlot = useCallback((slot: TimeSlot) => {
    setSelectedSlot(slot);
    setStep('consent');
  }, []);

  const confirmBooking = useCallback(async () => {
    if (!selectedDoctor || !consentGiven || !mode) return;
    setStep('confirming');
    setError(null);
    try {
      const appt = await bookAppointment(
        selectedDoctor,
        mode,
        selectedSlot,
        attachedFiles,
        aiReport,
        scanType,
        consentGiven,
        patientName
      );
      setAppointment(appt);
      setStep('confirmed');
    } catch (e: any) {
      setError(e.message || 'Booking failed. Please try again.');
      setStep('consent');
    }
  }, [selectedDoctor, consentGiven, mode, selectedSlot, aiReport, scanType, attachedFiles, patientName]);

  const reset = useCallback(() => {
    setStep('select-mode');
    setMode(null);
    setSelectedDoctor(null);
    setSelectedSlot(null);
    setConsentGiven(false);
    setAppointment(null);
    setError(null);
  }, []);

  const goBack = useCallback(() => {
    if (step === 'select-doctor') setStep('select-mode');
    else if (step === 'doctor-profile') setStep('select-doctor');
    else if (step === 'select-slot') setStep('doctor-profile');
    else if (step === 'consent') setStep(mode === 'verify' ? 'doctor-profile' : 'select-slot');
  }, [step, mode]);

  return {
    step,
    mode,
    selectedDoctor,
    selectedSlot,
    consentGiven,
    appointment,
    error,
    attachedFiles,
    selectMode,
    selectDoctor,
    proceedToSlot,
    selectSlot,
    setConsentGiven,
    confirmBooking,
    reset,
    goBack,
  };
}
