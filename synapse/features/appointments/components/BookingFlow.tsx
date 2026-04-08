"use client";

import React, { useState, useEffect } from 'react';
import { useBooking } from '../hooks/useBooking';
import { useDoctors } from '../hooks/useDoctors';
import { useGeolocation } from '../hooks/useGeolocation';
import { AppointmentMode } from '../types/appointment';
import { DoctorList } from './DoctorList';
import { DoctorProfile } from './DoctorProfile';
import { DoctorMapView } from './DoctorMapView';
import { ConsentScreen } from './ConsentScreen';
import { BookingConfirmation } from './BookingConfirmation';
import { Doctor } from '../types/doctor';
import { 
  X, ChevronLeft, List, Map as MapIcon, CheckCircle, Video, MapPin, Loader2
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface Props {
  aiReport: string;
  scanType: string;
  uploadedFileName: string;
  patientName: string;
  initialMode?: AppointmentMode;
  onClose: () => void;
}

const STEP_LABELS: Record<string, string> = {
  'select-mode': 'Choose Option',
  'select-doctor': 'Select Doctor',
  'doctor-profile': 'Doctor Profile',
  'select-slot': 'Pick Time Slot',
  'consent': 'Confirm & Consent',
  'confirming': 'Confirming',
  'confirmed': 'Confirmed!',
};

const STEP_ORDER = ['select-mode', 'select-doctor', 'doctor-profile', 'select-slot', 'consent', 'confirming', 'confirmed'];

export function BookingFlow({ aiReport, scanType, uploadedFileName, patientName, initialMode, onClose }: Props) {
  const booking = useBooking(aiReport, scanType, uploadedFileName, patientName);
  const { doctors, loading, load } = useDoctors();
  const { coords } = useGeolocation();
  const [viewMode, setViewMode] = useState<'list' | 'map'>('list');
  const [profileDoctor, setProfileDoctor] = useState<Doctor | null>(null);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    if (initialMode) {
      booking.selectMode(initialMode);
    }
  }, [initialMode]);

  const stepIdx = STEP_ORDER.indexOf(booking.step);
  const totalSteps = 5;

  const handleViewProfile = (doc: Doctor) => {
    setProfileDoctor(doc);
    booking.selectDoctor(doc);
  };

  const handleSelectFromProfile = (doc: Doctor) => {
    booking.selectDoctor(doc);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/60 backdrop-blur-md overflow-y-auto py-6">
      <motion.div
        initial={{ opacity: 0, scale: 0.96, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.96, y: 20 }}
        className="w-full max-w-3xl mx-4 bg-slate-950 rounded-3xl border border-white/10 shadow-2xl overflow-hidden"
      >
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/5 bg-slate-900/50">
          <div>
            <h2 className="text-lg font-black text-slate-100">Book Doctor Appointment</h2>
            <p className="text-xs text-slate-400 mt-0.5">{STEP_LABELS[booking.step]}</p>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 hover:text-slate-200 hover:bg-slate-700 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Progress Bar */}
        {booking.step !== 'confirmed' && (
          <div className="px-6 pt-4">
            <div className="flex items-center gap-2 mb-1">
              {['select-doctor', 'doctor-profile', 'select-slot', 'consent', 'confirmed'].map((s, i) => (
                <React.Fragment key={s}>
                  <div className={`h-1.5 flex-1 rounded-full transition-all ${stepIdx > i ? 'bg-blue-500' : stepIdx === i + 1 ? 'bg-blue-400' : 'bg-slate-800'}`} />
                </React.Fragment>
              ))}
            </div>
          </div>
        )}

        {/* Body */}
        <div className="p-6">
          <AnimatePresence mode="wait">
            {/* STEP: Select Mode */}
            {booking.step === 'select-mode' && (
              <motion.div key="select-mode" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }} className="space-y-5">
                <div>
                  <h3 className="text-base font-bold text-slate-200">How would you like to proceed?</h3>
                  <p className="text-sm text-slate-400 mt-1">Your AI scan report and scan file will be automatically shared with the doctor.</p>
                </div>
                <div className="grid grid-cols-1 gap-3">
                  {[
                    {
                      mode: 'verify' as AppointmentMode,
                      icon: CheckCircle,
                      emoji: '✅',
                      title: 'Verify Result by Doctor',
                      desc: 'Get a doctor to review and verify your AI-generated diagnostic report. No time slot needed.',
                      color: 'from-emerald-600/20 to-emerald-600/5',
                      border: 'border-emerald-500/30 hover:border-emerald-400/60',
                      iconColor: 'text-emerald-400',
                      badge: 'No Slot Needed',
                      badgeColor: 'bg-emerald-500/20 text-emerald-300',
                    },
                    {
                      mode: 'online' as AppointmentMode,
                      icon: Video,
                      emoji: '🎥',
                      title: 'Book Online Appointment',
                      desc: 'Schedule a secure video consultation with your chosen specialist.',
                      color: 'from-blue-600/20 to-blue-600/5',
                      border: 'border-blue-500/30 hover:border-blue-400/60',
                      iconColor: 'text-blue-400',
                      badge: 'Video Call',
                      badgeColor: 'bg-blue-500/20 text-blue-300',
                    },
                    {
                      mode: 'offline' as AppointmentMode,
                      icon: MapPin,
                      emoji: '🏥',
                      title: 'Book In-Person Appointment',
                      desc: 'Schedule a visit to the doctor\'s clinic with your scans and AI report.',
                      color: 'from-purple-600/20 to-purple-600/5',
                      border: 'border-purple-500/30 hover:border-purple-400/60',
                      iconColor: 'text-purple-400',
                      badge: 'At Clinic',
                      badgeColor: 'bg-purple-500/20 text-purple-300',
                    },
                  ].map((opt, i) => (
                    <motion.button
                      key={opt.mode}
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.07 }}
                      onClick={() => booking.selectMode(opt.mode)}
                      className={`group relative text-left p-4 rounded-2xl bg-gradient-to-br ${opt.color} border ${opt.border} hover:scale-[1.01] active:scale-[0.99] transition-all duration-200 shadow-md flex items-center gap-4`}
                    >
                      <div className={`w-11 h-11 rounded-xl bg-white/5 flex items-center justify-center flex-shrink-0 ${opt.iconColor}`}>
                        <opt.icon className="w-5 h-5" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-0.5">
                          <h4 className="text-sm font-bold text-slate-100">{opt.title}</h4>
                          <span className={`text-[9px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-full ${opt.badgeColor}`}>{opt.badge}</span>
                        </div>
                        <p className="text-xs text-slate-400 leading-relaxed">{opt.desc}</p>
                      </div>
                      <div className="text-slate-500 group-hover:text-slate-300 group-hover:translate-x-1 transition-all flex-shrink-0">
                        →
                      </div>
                    </motion.button>
                  ))}
                </div>
              </motion.div>
            )}

            {/* STEP: Doctor Discovery */}
            {booking.step === 'select-doctor' && (
              <motion.div key="select-doctor" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
                <div className="flex items-center gap-3 mb-5">
                  <h3 className="text-base font-bold text-slate-200 flex-1">Find a Specialist</h3>
                  <div className="flex bg-slate-900 rounded-xl border border-white/5 p-1 gap-1">
                    <button
                      onClick={() => setViewMode('list')}
                      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${viewMode === 'list' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
                    >
                      <List className="w-3.5 h-3.5" /> List
                    </button>
                    <button
                      onClick={() => setViewMode('map')}
                      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${viewMode === 'map' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
                    >
                      <MapIcon className="w-3.5 h-3.5" /> Map
                    </button>
                  </div>
                </div>
                {viewMode === 'list' ? (
                  <DoctorList
                    onSelect={booking.selectDoctor}
                    onViewProfile={handleViewProfile}
                  />
                ) : (
                  <DoctorMapView
                    doctors={doctors}
                    onSelect={booking.selectDoctor}
                    userLat={coords?.lat}
                    userLng={coords?.lng}
                  />
                )}
              </motion.div>
            )}

            {/* STEP: Doctor Profile */}
            {booking.step === 'doctor-profile' && booking.selectedDoctor && booking.mode && (
              <motion.div key="doctor-profile" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
                <DoctorProfile
                  doctor={booking.selectedDoctor}
                  mode={booking.mode}
                  onSelectSlot={booking.selectSlot}
                  onProceedVerify={booking.proceedToSlot}
                  onBack={booking.goBack}
                />
              </motion.div>
            )}

            {/* STEP: Consent */}
            {booking.step === 'consent' && booking.selectedDoctor && booking.mode && (
              <motion.div key="consent" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
                <ConsentScreen
                  doctor={booking.selectedDoctor}
                  mode={booking.mode}
                  attachedFiles={booking.attachedFiles}
                  consentGiven={booking.consentGiven}
                  onConsentChange={booking.setConsentGiven}
                  onConfirm={booking.confirmBooking}
                  onBack={booking.goBack}
                  loading={false}
                  error={booking.error}
                />
              </motion.div>
            )}

            {/* STEP: Confirming */}
            {booking.step === 'confirming' && (
              <motion.div key="confirming" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col items-center justify-center py-20 gap-4">
                <div className="relative">
                  <div className="w-20 h-20 border-4 border-blue-500/10 border-t-blue-500 rounded-full animate-spin" />
                  <Loader2 className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 text-blue-400 animate-pulse" />
                </div>
                <div className="text-center">
                  <p className="text-lg font-bold text-slate-200">Confirming Your Appointment</p>
                  <p className="text-sm text-slate-400 mt-1">Securely sending your medical files to the doctor...</p>
                </div>
              </motion.div>
            )}

            {/* STEP: Confirmed */}
            {booking.step === 'confirmed' && booking.appointment && (
              <motion.div key="confirmed" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
                <BookingConfirmation
                  appointment={booking.appointment}
                  onReset={() => { booking.reset(); onClose(); }}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </div>
  );
}
