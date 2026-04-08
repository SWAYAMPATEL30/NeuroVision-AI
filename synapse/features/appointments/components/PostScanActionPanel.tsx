"use client";

import React from 'react';
import { AppointmentMode } from '../types/appointment';
import { CheckCircle, Video, MapPin, Paperclip, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

interface Props {
  onSelect: (mode: AppointmentMode) => void;
  scanType: string;
  uploadedFileName: string;
}

const OPTIONS = [
  {
    mode: 'verify' as AppointmentMode,
    icon: CheckCircle,
    emoji: '✅',
    title: 'Verify Result by Doctor',
    desc: 'Get a doctor to review and verify your AI-generated diagnostic report.',
    color: 'from-emerald-600/20 to-emerald-600/5',
    border: 'border-emerald-500/30',
    iconColor: 'text-emerald-400',
    badge: 'No time slot needed',
    badgeColor: 'bg-emerald-500/20 text-emerald-300',
  },
  {
    mode: 'online' as AppointmentMode,
    icon: Video,
    emoji: '🎥',
    title: 'Book Online Appointment',
    desc: 'Schedule a secure video consultation with your chosen specialist.',
    color: 'from-blue-600/20 to-blue-600/5',
    border: 'border-blue-500/30',
    iconColor: 'text-blue-400',
    badge: 'Video Call',
    badgeColor: 'bg-blue-500/20 text-blue-300',
  },
  {
    mode: 'offline' as AppointmentMode,
    icon: MapPin,
    emoji: '🏥',
    title: 'Book In-Person Appointment',
    desc: 'Visit the doctor\'s clinic with your scans and AI report ready.',
    color: 'from-purple-600/20 to-purple-600/5',
    border: 'border-purple-500/30',
    iconColor: 'text-purple-400',
    badge: 'At Clinic',
    badgeColor: 'bg-purple-500/20 text-purple-300',
  },
];

export function PostScanActionPanel({ onSelect, scanType, uploadedFileName }: Props) {
  return (
    <div className="mt-8 space-y-5">
      <div className="flex items-start gap-3 p-4 bg-slate-900/60 rounded-2xl border border-white/5">
        <Paperclip className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
        <div>
          <p className="text-sm font-semibold text-slate-200">Files ready to share with your doctor</p>
          <p className="text-xs text-slate-400 mt-1">
            📊 AI Diagnostic Report ({scanType || 'Medical Scan'})
            {uploadedFileName && <> · 🖼️ {uploadedFileName}</>}
          </p>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-bold text-slate-100 mb-1">What would you like to do next?</h3>
        <p className="text-sm text-slate-400">Your AI report and scan will be automatically shared with the doctor you choose.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {OPTIONS.map((opt, i) => (
          <motion.button
            key={opt.mode}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08 }}
            onClick={() => onSelect(opt.mode)}
            className={`relative group text-left p-5 rounded-2xl bg-gradient-to-br ${opt.color} border ${opt.border} hover:scale-[1.02] active:scale-[0.99] transition-all duration-200 shadow-lg`}
          >
            <div className={`w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center mb-3 ${opt.iconColor}`}>
              <opt.icon className="w-5 h-5" />
            </div>
            <span className={`text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-full ${opt.badgeColor} mb-2 inline-block`}>
              {opt.badge}
            </span>
            <h4 className="text-sm font-bold text-slate-100 leading-snug mt-1">{opt.title}</h4>
            <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">{opt.desc}</p>
            <ArrowRight className="absolute bottom-4 right-4 w-4 h-4 text-slate-500 group-hover:text-slate-300 group-hover:translate-x-1 transition-all" />
          </motion.button>
        ))}
      </div>
    </div>
  );
}
