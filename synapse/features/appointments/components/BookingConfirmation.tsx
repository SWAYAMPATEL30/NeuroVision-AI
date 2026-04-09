"use client";

import React from 'react';
import { Appointment } from '../types/appointment';
import { 
  CheckCircle2, Video, MapPin, Paperclip, Calendar, Clock, 
  Download, RotateCcw, CalendarPlus, ArrowRight
} from 'lucide-react';
import { motion } from 'framer-motion';

interface Props {
  appointment: Appointment;
  onReset: () => void;
}

const MODE_LABELS = {
  verify: { label: 'Doctor Verification', icon: CheckCircle2, color: 'text-emerald-400', bg: 'bg-emerald-500/20', border: 'border-emerald-500/30' },
  online: { label: 'Online Video Call', icon: Video, color: 'text-blue-400', bg: 'bg-blue-500/20', border: 'border-blue-500/30' },
  offline: { label: 'In-Person Visit', icon: MapPin, color: 'text-purple-400', bg: 'bg-purple-500/20', border: 'border-purple-500/30' },
};

function buildGoogleCalendarUrl(appt: Appointment): string {
  if (!appt.date || !appt.time) return '#';
  const base = 'https://calendar.google.com/calendar/render?action=TEMPLATE';
  const params = new URLSearchParams();
  const modeLabel = MODE_LABELS[appt.mode].label;
  params.set('text', `${modeLabel} with ${appt.doctorName}`);
  params.set('details', `NeuroVision AI appointment. ${appt.aiReport ? 'AI Report attached.' : ''}`);
  if (appt.clinicAddress && appt.mode === 'offline') params.set('location', appt.clinicAddress);
  
  // Build date
  const [year, month, day] = appt.date.split('-').map(Number);
  let hours = 9, minutes = 0;
  const match = appt.time.match(/^(\d{1,2}):(\d{2})\s*(AM|PM)$/i);
  if (match) {
    hours = parseInt(match[1]);
    minutes = parseInt(match[2]);
    if (match[3].toUpperCase() === 'PM' && hours !== 12) hours += 12;
    if (match[3].toUpperCase() === 'AM' && hours === 12) hours = 0;
  }
  const start = new Date(year, month - 1, day, hours, minutes);
  const end = new Date(start.getTime() + 60 * 60 * 1000);
  const fmt = (d: Date) => d.toISOString().replace(/[-:]/g, '').replace(/\..+/, '');
  params.set('dates', `${fmt(start)}Z/${fmt(end)}Z`);
  return `${base}&${params.toString()}`;
}

export function BookingConfirmation({ appointment, onReset }: Props) {
  const modeInfo = MODE_LABELS[appointment.mode];
  const ModeIcon = modeInfo.icon;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.96 }}
      animate={{ opacity: 1, scale: 1 }}
      className="space-y-6"
    >
      {/* Success Header */}
      <div className="text-center py-8 space-y-4">
        <div className="relative mx-auto w-20 h-20">
          <div className="absolute inset-0 bg-emerald-500/20 rounded-full animate-ping" />
          <div className="relative w-20 h-20 bg-emerald-500/20 rounded-full flex items-center justify-center border border-emerald-500/40">
            <CheckCircle2 className="w-10 h-10 text-emerald-400" />
          </div>
        </div>
        <div>
          <h2 className="text-2xl font-black text-slate-100">Appointment Confirmed!</h2>
          <p className="text-slate-400 mt-1">You'll receive a confirmation shortly.</p>
          <p className="text-xs text-slate-500 mt-1 font-mono">ID: {appointment.id}</p>
        </div>
      </div>

      {/* Card Summary */}
      <div className="bg-slate-900/60 rounded-2xl border border-white/5 overflow-hidden">
        {/* Doctor Row */}
        <div className="p-5 flex items-center gap-4 border-b border-white/5">
          <img
            src={appointment.doctorPhoto}
            alt={appointment.doctorName}
            className="w-14 h-14 rounded-2xl object-cover"
            onError={(e) => { (e.target as HTMLImageElement).src = 'https://via.placeholder.com/56x56/1e293b/94a3b8?text=Dr'; }}
          />
          <div>
            <h3 className="font-bold text-slate-100 text-lg">{appointment.doctorName}</h3>
            <p className="text-blue-400 text-sm">{appointment.doctorSpecialization}</p>
          </div>
        </div>

        {/* Details Grid */}
        <div className="grid grid-cols-2 gap-px bg-white/5">
          <div className="bg-slate-900/60 p-4">
            <p className="text-[10px] uppercase tracking-widest text-slate-500 mb-1">Appointment Type</p>
            <div className={`flex items-center gap-2 ${modeInfo.color}`}>
              <ModeIcon className="w-4 h-4" />
              <span className="font-bold text-sm">{modeInfo.label}</span>
            </div>
          </div>
          <div className="bg-slate-900/60 p-4">
            <p className="text-[10px] uppercase tracking-widest text-slate-500 mb-1">Status</p>
            <span className="inline-flex items-center gap-1.5 text-sm font-bold text-emerald-400">
              <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
              Confirmed
            </span>
          </div>
          {appointment.date && (
            <div className="bg-slate-900/60 p-4">
              <p className="text-[10px] uppercase tracking-widest text-slate-500 mb-1">Date</p>
              <div className="flex items-center gap-2 text-slate-200 font-semibold text-sm">
                <Calendar className="w-4 h-4 text-slate-400" />
                {new Date(appointment.date + 'T00:00:00').toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'long' })}
              </div>
            </div>
          )}
          {appointment.time && (
            <div className="bg-slate-900/60 p-4">
              <p className="text-[10px] uppercase tracking-widest text-slate-500 mb-1">Time</p>
              <div className="flex items-center gap-2 text-slate-200 font-semibold text-sm">
                <Clock className="w-4 h-4 text-slate-400" />
                {appointment.time}
              </div>
            </div>
          )}
          {appointment.mode === 'offline' && appointment.clinicAddress && (
            <div className="bg-slate-900/60 p-4 col-span-2">
              <p className="text-[10px] uppercase tracking-widest text-slate-500 mb-1">Clinic Address</p>
              <div className="flex items-start gap-2 text-slate-300 text-sm">
                <MapPin className="w-4 h-4 text-slate-400 mt-0.5 flex-shrink-0" />
                {appointment.clinicAddress}
              </div>
            </div>
          )}
        </div>

        {/* Files Attached */}
        <div className="p-5 border-t border-white/5">
          <div className="flex items-center gap-2 mb-3">
            <Paperclip className="w-4 h-4 text-blue-400" />
            <span className="text-sm font-bold text-slate-200">Files Attached to Doctor</span>
            <span className="text-[10px] px-2 py-0.5 bg-emerald-500/20 text-emerald-400 rounded-full border border-emerald-500/30 font-bold">
              ✓ Securely Shared
            </span>
          </div>
          <div className="space-y-2">
            {appointment.attachedFiles.map((file, i) => (
              <div key={i} className="flex items-center gap-2.5 py-2 px-3 bg-slate-800/50 rounded-xl border border-white/5">
                <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center text-base">
                  {file.type === 'xray' ? '🖼️' : '📊'}
                </div>
                <span className="text-sm text-slate-300 font-medium">{file.name}</span>
                <span className="ml-auto text-[10px] uppercase text-slate-500 font-bold">{file.type}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {appointment.date && appointment.time && (
          <a
            href={buildGoogleCalendarUrl(appointment)}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center gap-2 py-3 px-4 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold rounded-xl border border-white/5 transition-colors text-sm"
          >
            <CalendarPlus className="w-4 h-4 text-blue-400" />
            Add to Calendar
          </a>
        )}
        {appointment.videoCallUrl && appointment.mode === 'online' && (
          <a
            href={appointment.videoCallUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center gap-2 py-3 px-4 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl transition-colors text-sm shadow-lg shadow-blue-900/30"
          >
            <Video className="w-4 h-4" />
            Join Video Call
            <ArrowRight className="w-4 h-4" />
          </a>
        )}
        <button
          onClick={onReset}
          className={`flex items-center justify-center gap-2 py-3 px-4 bg-slate-900/60 hover:bg-slate-800 text-slate-400 font-semibold rounded-xl border border-white/5 transition-colors text-sm ${(!appointment.date || !appointment.time) && !appointment.videoCallUrl ? 'col-span-2' : ''}`}
        >
          <RotateCcw className="w-4 h-4" />
          Book Another Appointment
        </button>
      </div>
    </motion.div>
  );
}
