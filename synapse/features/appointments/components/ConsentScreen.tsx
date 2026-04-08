"use client";

import React from 'react';
import { Doctor } from '../types/doctor';
import { AppointmentMode, AttachedFile } from '../types/appointment';
import { Shield, Paperclip, CheckCircle, Loader2, ChevronLeft, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

interface Props {
  doctor: Doctor;
  mode: AppointmentMode;
  attachedFiles: AttachedFile[];
  consentGiven: boolean;
  onConsentChange: (val: boolean) => void;
  onConfirm: () => void;
  onBack: () => void;
  loading: boolean;
  error: string | null;
}

const MODE_LABELS: Record<AppointmentMode, string> = {
  verify: 'Doctor Verification (Report sent for review)',
  online: 'Online Video Call Appointment',
  offline: 'In-Person Clinic Visit',
};

export function ConsentScreen({ doctor, mode, attachedFiles, consentGiven, onConsentChange, onConfirm, onBack, loading, error }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-5"
    >
      <button onClick={onBack} className="flex items-center gap-2 text-sm text-slate-400 hover:text-slate-200 transition-colors">
        <ChevronLeft className="w-4 h-4" />
        Back
      </button>

      <div className="bg-slate-900/60 rounded-2xl border border-white/5 p-6 space-y-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center">
            <Shield className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <h3 className="font-bold text-slate-100">Privacy & Consent</h3>
            <p className="text-xs text-slate-400">Review before sharing your medical data</p>
          </div>
        </div>

        {/* Doctor Summary */}
        <div className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-xl border border-white/5">
          <img
            src={doctor.photo}
            alt={doctor.name}
            className="w-10 h-10 rounded-xl object-cover"
            onError={(e) => { (e.target as HTMLImageElement).src = 'https://via.placeholder.com/40x40/1e293b/94a3b8?text=Dr'; }}
          />
          <div>
            <p className="font-semibold text-slate-200 text-sm">{doctor.name}</p>
            <p className="text-xs text-slate-400">{doctor.specialization} · {MODE_LABELS[mode]}</p>
          </div>
        </div>

        {/* Files Being Shared */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Paperclip className="w-4 h-4 text-blue-400" />
            <h4 className="text-sm font-bold text-slate-300">Files that will be shared:</h4>
          </div>
          <div className="space-y-2">
            {attachedFiles.map((file, i) => (
              <div key={i} className="flex items-center gap-3 p-3 bg-slate-800/30 rounded-xl border border-white/5">
                <span className="text-xl">{file.type === 'xray' ? '🖼️' : '📊'}</span>
                <div>
                  <p className="text-sm font-medium text-slate-200">{file.name}</p>
                  <p className="text-xs text-slate-500 capitalize">{file.type === 'xray' ? 'Uploaded Scan File' : 'AI Diagnostic Report'}</p>
                </div>
                <CheckCircle className="w-4 h-4 text-emerald-400 ml-auto" />
              </div>
            ))}
          </div>
        </div>

        {/* Consent Checkbox */}
        <label className="flex items-start gap-3 cursor-pointer group">
          <div className="mt-0.5">
            <input
              type="checkbox"
              checked={consentGiven}
              onChange={e => onConsentChange(e.target.checked)}
              className="sr-only"
            />
            <div className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
              consentGiven ? 'bg-blue-600 border-blue-500' : 'bg-slate-800 border-white/20 group-hover:border-blue-500/50'
            }`}>
              {consentGiven && (
                <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              )}
            </div>
          </div>
          <p className="text-sm text-slate-300 leading-relaxed">
            I consent to sharing my uploaded scan files and AI-generated diagnostic report with{' '}
            <span className="font-bold text-slate-100">{doctor.name}</span> for medical consultation and verification purposes.
            I understand this data will be handled securely and used solely for my healthcare.
          </p>
        </label>

        {/* Error */}
        {error && (
          <div className="flex items-center gap-2 p-3 bg-red-500/10 rounded-xl border border-red-500/20 text-sm text-red-300">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            {error}
          </div>
        )}

        {/* Confirm Button */}
        <button
          onClick={onConfirm}
          disabled={!consentGiven || loading}
          className="w-full py-4 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:text-slate-500 disabled:cursor-not-allowed text-white font-bold rounded-xl flex items-center justify-center gap-2 transition-all shadow-lg shadow-blue-900/30 text-sm"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Confirming Appointment...
            </>
          ) : (
            <>
              <CheckCircle className="w-4 h-4" />
              Confirm Appointment
            </>
          )}
        </button>
      </div>
    </motion.div>
  );
}
