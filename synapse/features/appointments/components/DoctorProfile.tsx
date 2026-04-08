"use client";

import React, { useState } from 'react';
import { Doctor, TimeSlot } from '../types/doctor';
import { AppointmentMode } from '../types/appointment';
import { 
  Star, MapPin, Video, Building2, Award, Calendar, Clock, 
  ChevronLeft, ArrowRight, CheckCircle, MessageSquare
} from 'lucide-react';
import { motion } from 'framer-motion';

interface Props {
  doctor: Doctor;
  mode: AppointmentMode;
  onSelectSlot: (slot: TimeSlot) => void;
  onProceedVerify: () => void;
  onBack: () => void;
}

function StarRating({ rating, size = 'sm' }: { rating: number; size?: 'sm' | 'lg' }) {
  const w = size === 'lg' ? 'w-5 h-5' : 'w-3.5 h-3.5';
  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map(star => (
        <svg key={star} className={`${w} ${star <= Math.round(rating) ? 'text-yellow-400' : 'text-slate-600'}`} fill="currentColor" viewBox="0 0 20 20">
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
        </svg>
      ))}
    </div>
  );
}

function SlotPicker({ slots, onSelect }: { slots: TimeSlot[]; onSelect: (slot: TimeSlot) => void }) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  
  const grouped = slots.reduce((acc, slot) => {
    if (!acc[slot.date]) acc[slot.date] = [];
    acc[slot.date].push(slot);
    return acc;
  }, {} as Record<string, TimeSlot[]>);

  return (
    <div className="space-y-4">
      {Object.entries(grouped).map(([date, daySlots]) => (
        <div key={date} className="space-y-2">
          <h4 className="text-xs font-bold uppercase tracking-widest text-slate-500">
            {new Date(date + 'T00:00:00').toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'short' })}
          </h4>
          <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
            {daySlots.map(slot => (
              <button
                key={slot.id}
                disabled={!slot.available}
                onClick={() => { setSelectedId(slot.id); onSelect(slot); }}
                className={`py-2 px-3 rounded-xl text-xs font-semibold border transition-all ${
                  !slot.available
                    ? 'bg-slate-900/30 border-white/5 text-slate-600 cursor-not-allowed line-through'
                    : selectedId === slot.id
                    ? 'bg-blue-600 border-blue-500 text-white shadow-lg shadow-blue-900/30'
                    : 'bg-slate-800/50 border-white/5 text-slate-300 hover:border-blue-500/40 hover:bg-slate-800'
                }`}
              >
                {slot.time}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

export function DoctorProfile({ doctor, mode, onSelectSlot, onProceedVerify, onBack }: Props) {
  const [activeTab, setActiveTab] = useState<'about' | 'reviews' | 'slots'>('about');

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="space-y-6"
    >
      {/* Back Button */}
      <button onClick={onBack} className="flex items-center gap-2 text-sm text-slate-400 hover:text-slate-200 transition-colors">
        <ChevronLeft className="w-4 h-4" />
        Back to Doctors
      </button>

      {/* Doctor Hero */}
      <div className="bg-slate-900/50 rounded-2xl border border-white/5 overflow-hidden">
        <div className="h-24 bg-gradient-to-r from-blue-600/20 via-cyan-600/10 to-blue-600/5" />
        <div className="px-6 pb-6 -mt-10">
          <div className="flex items-end gap-5">
            <img
              src={doctor.photo}
              alt={doctor.name}
              className="w-20 h-20 rounded-2xl border-4 border-slate-900 object-cover"
              onError={(e) => { (e.target as HTMLImageElement).src = 'https://via.placeholder.com/80x80/1e293b/94a3b8?text=Dr'; }}
            />
            <div className="flex-1 pb-1">
              <h2 className="text-xl font-black text-slate-100">{doctor.name}</h2>
              <p className="text-blue-400 font-semibold">{doctor.specialization}</p>
            </div>
          </div>

          {/* Rating + Chips */}
          <div className="mt-4 flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2">
              <StarRating rating={doctor.avgRating} size="lg" />
              <span className="text-lg font-black text-yellow-400">{doctor.avgRating}</span>
              <span className="text-sm text-slate-500">({doctor.reviewCount} reviews)</span>
            </div>
            {doctor.onlineAvailable && (
              <span className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-wide px-2.5 py-1 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30">
                <Video className="w-3 h-3" /> Online
              </span>
            )}
            {doctor.offlineAvailable && (
              <span className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-wide px-2.5 py-1 rounded-full bg-slate-700/50 text-slate-400 border border-slate-600/50">
                <Building2 className="w-3 h-3" /> Offline
              </span>
            )}
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-3 gap-3 mt-5">
            {[
              { label: 'Experience', value: `${doctor.experience}+ yrs` },
              { label: 'Consult Fee', value: `₹${doctor.consultationFee}` },
              { label: 'Patients', value: `${doctor.reviewCount * 8}+` },
            ].map(stat => (
              <div key={stat.label} className="bg-slate-800/50 rounded-xl p-3 text-center border border-white/5">
                <p className="text-lg font-black text-slate-100">{stat.value}</p>
                <p className="text-[10px] uppercase tracking-widest text-slate-500">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex bg-slate-900/50 rounded-xl border border-white/5 p-1 gap-1">
        {(['about', 'reviews', 'slots'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-1 py-2 text-sm font-semibold rounded-lg transition-all capitalize ${
              activeTab === tab ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            {tab === 'slots' ? 'Book Slot' : tab}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="bg-slate-900/40 rounded-2xl border border-white/5 p-6">
        {activeTab === 'about' && (
          <div className="space-y-5">
            <div>
              <h3 className="text-sm font-bold text-slate-300 mb-2">About</h3>
              <p className="text-sm text-slate-400 leading-relaxed">{doctor.bio}</p>
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-300 mb-2">Education</h3>
              <div className="flex items-start gap-3">
                <Award className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-sm font-semibold text-slate-200">{doctor.degree}</p>
                  <p className="text-xs text-slate-400">{doctor.university} · {doctor.graduationYear}</p>
                </div>
              </div>
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-300 mb-2">Certifications</h3>
              <div className="flex flex-wrap gap-2">
                {doctor.certifications.map(cert => (
                  <span key={cert} className="text-xs px-3 py-1 bg-slate-800 text-slate-300 rounded-full border border-white/5">
                    {cert}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-300 mb-2">Location</h3>
              <div className="flex items-start gap-2 text-sm text-slate-400">
                <MapPin className="w-4 h-4 text-slate-400 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-semibold text-slate-300">{doctor.clinicName}</p>
                  <p>{doctor.address}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'reviews' && (
          <div className="space-y-4">
            {doctor.reviews.map(review => (
              <div key={review.id} className="border-b border-white/5 pb-4 last:border-0 last:pb-0">
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-full bg-blue-500/20 flex items-center justify-center text-xs font-bold text-blue-400">
                      {review.patientName[0]}
                    </div>
                    <span className="text-sm font-semibold text-slate-200">{review.patientName}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <StarRating rating={review.rating} />
                    <span className="text-xs text-slate-500">{review.date}</span>
                  </div>
                </div>
                <p className="text-sm text-slate-400 leading-relaxed pl-9">{review.comment}</p>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'slots' && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 p-3 bg-blue-500/10 rounded-xl border border-blue-500/20">
              <Calendar className="w-4 h-4 text-blue-400 flex-shrink-0" />
              <p className="text-xs text-blue-300">
                {mode === 'verify' ? 'No slot needed — the doctor will review your report at their convenience.' : 'Select a time that works for you.'}
              </p>
            </div>
            {mode !== 'verify' ? (
              <SlotPicker slots={doctor.timeSlots} onSelect={onSelectSlot} />
            ) : (
              <button
                onClick={onProceedVerify}
                className="w-full py-4 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl flex items-center justify-center gap-2 transition-colors shadow-lg shadow-blue-900/30"
              >
                <CheckCircle className="w-5 h-5" />
                Proceed with Verification Request
                <ArrowRight className="w-4 h-4" />
              </button>
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
}
