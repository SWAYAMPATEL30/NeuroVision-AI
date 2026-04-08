"use client";

import React from 'react';
import { Doctor } from '../types/doctor';
import { Star, MapPin, Video, Building2, ArrowRight, Clock } from 'lucide-react';
import { motion } from 'framer-motion';

interface Props {
  doctor: Doctor;
  index: number;
  onSelect: (doctor: Doctor) => void;
  onViewProfile: (doctor: Doctor) => void;
}

const AVAILABILITY_COLORS: Record<Doctor['availabilityColor'], string> = {
  green: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  yellow: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  grey: 'bg-slate-600/20 text-slate-400 border-slate-500/30',
};

const AVAILABILITY_DOT: Record<Doctor['availabilityColor'], string> = {
  green: 'bg-emerald-500',
  yellow: 'bg-yellow-500',
  grey: 'bg-slate-500',
};

const AVAILABILITY_LABEL: Record<Doctor['availabilityColor'], string> = {
  green: 'Available Today',
  yellow: 'Next 2 Days',
  grey: 'Next Week+',
};

function StarRating({ rating }: { rating: number }) {
  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map(star => (
        <svg
          key={star}
          className={`w-3.5 h-3.5 ${star <= Math.round(rating) ? 'text-yellow-400' : 'text-slate-600'}`}
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
        </svg>
      ))}
    </div>
  );
}

export function DoctorCard({ doctor, index, onSelect, onViewProfile }: Props) {
  const availClass = AVAILABILITY_COLORS[doctor.availabilityColor];
  const dotClass = AVAILABILITY_DOT[doctor.availabilityColor];
  const availLabel = AVAILABILITY_LABEL[doctor.availabilityColor];

  const availSlots = doctor.timeSlots.filter(s => s.available).length;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="group bg-slate-900/50 border border-white/5 rounded-2xl p-5 hover:border-white/10 hover:bg-slate-900/80 transition-all duration-200 flex flex-col gap-4"
    >
      {/* Top Row */}
      <div className="flex items-start gap-4">
        <div className="relative flex-shrink-0">
          <img
            src={doctor.photo}
            alt={doctor.name}
            className="w-16 h-16 rounded-2xl object-cover"
            onError={(e) => { (e.target as HTMLImageElement).src = 'https://via.placeholder.com/64x64/1e293b/94a3b8?text=Dr'; }}
          />
          <div className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-slate-900 ${dotClass}`} />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-bold text-slate-100 text-base truncate">{doctor.name}</h3>
          <p className="text-sm text-blue-400 font-medium">{doctor.specialization}</p>
          <p className="text-xs text-slate-500 mt-0.5">{doctor.degree} · {doctor.university}</p>
          <div className="flex items-center gap-2 mt-1.5">
            <StarRating rating={doctor.avgRating} />
            <span className="text-xs font-bold text-yellow-400">{doctor.avgRating}</span>
            <span className="text-xs text-slate-500">({doctor.reviewCount} reviews)</span>
          </div>
        </div>
      </div>

      {/* Meta Chips */}
      <div className="flex flex-wrap gap-2">
        <span className={`flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wide px-2.5 py-1 rounded-full border ${availClass}`}>
          <span className={`w-1.5 h-1.5 rounded-full ${dotClass} animate-pulse`} />
          {availLabel}
        </span>
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
        <span className="text-[10px] font-bold uppercase tracking-wide px-2.5 py-1 rounded-full bg-slate-700/50 text-slate-400 border border-slate-600/50">
          {doctor.experience}yr exp
        </span>
      </div>

      {/* Location & Slots */}
      <div className="flex items-center justify-between text-xs text-slate-500">
        <span className="flex items-center gap-1.5 truncate">
          <MapPin className="w-3.5 h-3.5 flex-shrink-0 text-slate-400" />
          <span className="truncate">{doctor.clinicName}, {doctor.area}</span>
        </span>
        <span className="flex items-center gap-1 flex-shrink-0 ml-2">
          <Clock className="w-3.5 h-3.5 text-slate-400" />
          {availSlots} slots
        </span>
      </div>

      {/* Fee */}
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs text-slate-500">Consultation Fee</p>
          <p className="text-base font-bold text-slate-100">₹{doctor.consultationFee}</p>
        </div>
          <div className="flex gap-2">
          <a
            href={`/dashboard/doctors/${doctor.id}`}
            className="px-3 py-2 text-xs font-semibold text-slate-300 bg-slate-800 rounded-xl hover:bg-slate-700 transition-colors border border-white/5"
          >
            View Profile
          </a>
          <button
            onClick={() => onSelect(doctor)}
            className="px-4 py-2 text-xs font-bold text-white bg-blue-600 rounded-xl hover:bg-blue-500 transition-colors flex items-center gap-1.5 shadow-lg shadow-blue-900/30"
          >
            Book <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </motion.div>
  );
}
