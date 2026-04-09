"use client";

import React, { useEffect, useState } from 'react';
import { Doctor } from '../types/doctor';
import { DoctorCard } from './DoctorCard';
import { useDoctors } from '../hooks/useDoctors';
import { Search, SlidersHorizontal, Users } from 'lucide-react';

interface Props {
  onSelect: (doctor: Doctor) => void;
  onViewProfile: (doctor: Doctor) => void;
}

export function DoctorList({ onSelect, onViewProfile }: Props) {
  const { doctors, loading, load, filters, setFilters, specializations, cities } = useDoctors();
  const [search, setSearch] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  // Removed redundant load() as useDoctors hook already has a mount effect
  // useEffect(() => { load(); }, [load]);

  const filtered = doctors.filter(d =>
    search === '' ||
    d.name.toLowerCase().includes(search.toLowerCase()) ||
    d.specialization.toLowerCase().includes(search.toLowerCase()) ||
    d.city.toLowerCase().includes(search.toLowerCase())
  );

  // Group by city
  const grouped = filtered.reduce((acc, doc) => {
    if (!acc[doc.city]) acc[doc.city] = [];
    acc[doc.city].push(doc);
    return acc;
  }, {} as Record<string, Doctor[]>);

  return (
    <div className="space-y-6">
      {/* Search + Filter Bar */}
      <div className="flex gap-3 items-center">
        <div className="flex-1 relative">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search by name, specialty, or city..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-slate-900/60 border border-white/5 rounded-xl text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-blue-500/50 transition-colors"
          />
        </div>
        <button
          onClick={() => setShowFilters(f => !f)}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl border text-sm font-medium transition-colors ${showFilters ? 'bg-blue-600 border-blue-500 text-white' : 'bg-slate-900/60 border-white/5 text-slate-400 hover:text-slate-200'}`}
        >
          <SlidersHorizontal className="w-4 h-4" />
          Filters
        </button>
      </div>

      {/* Filter Panel */}
      {showFilters && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 p-4 bg-slate-900/40 rounded-2xl border border-white/5">
          <div>
            <label className="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-1.5 block">Specialization</label>
            <select
              value={filters.specialization}
              onChange={e => setFilters(f => ({ ...f, specialization: e.target.value }))}
              className="w-full px-3 py-2 bg-slate-800 border border-white/5 rounded-xl text-sm text-slate-200 focus:outline-none"
            >
              {specializations.map(s => (
                <option key={s} value={s}>{s === 'all' ? 'All Specialties' : s}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-1.5 block">City</label>
            <select
              value={filters.city}
              onChange={e => setFilters(f => ({ ...f, city: e.target.value }))}
              className="w-full px-3 py-2 bg-slate-800 border border-white/5 rounded-xl text-sm text-slate-200 focus:outline-none"
            >
              {cities.map(c => (
                <option key={c} value={c}>{c === 'all' ? 'All Cities' : c}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-1.5 block">Availability</label>
            <select
              value={filters.availability}
              onChange={e => setFilters(f => ({ ...f, availability: e.target.value as any }))}
              className="w-full px-3 py-2 bg-slate-800 border border-white/5 rounded-xl text-sm text-slate-200 focus:outline-none"
            >
              <option value="all">All Types</option>
              <option value="online">Online Only</option>
              <option value="offline">Offline Only</option>
            </select>
          </div>
          <div>
            <label className="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-1.5 block">Sort By</label>
            <select
              value={filters.sortBy}
              onChange={e => setFilters(f => ({ ...f, sortBy: e.target.value as any }))}
              className="w-full px-3 py-2 bg-slate-800 border border-white/5 rounded-xl text-sm text-slate-200 focus:outline-none"
            >
              <option value="rating">Highest Rating</option>
              <option value="nearest">Nearest Location</option>
              <option value="soonest">Earliest Available</option>
            </select>
          </div>
        </div>
      )}

      {/* Loading Skeletons */}
      {loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} className="bg-slate-900/50 border border-white/5 rounded-2xl p-5 animate-pulse space-y-4">
              <div className="flex gap-4">
                <div className="w-16 h-16 rounded-2xl bg-slate-800" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-slate-800 rounded w-3/4" />
                  <div className="h-3 bg-slate-800 rounded w-1/2" />
                  <div className="h-3 bg-slate-800 rounded w-2/3" />
                </div>
              </div>
              <div className="flex gap-2">
                <div className="h-6 w-24 bg-slate-800 rounded-full" />
                <div className="h-6 w-16 bg-slate-800 rounded-full" />
              </div>
              <div className="h-8 bg-slate-800 rounded-xl" />
              <div className="flex justify-between">
                <div className="h-8 w-24 bg-slate-800 rounded-xl" />
                <div className="flex gap-2">
                  <div className="h-8 w-20 bg-slate-800 rounded-xl" />
                  <div className="h-8 w-16 bg-slate-800 rounded-xl" />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {!loading && filtered.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 text-center space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-slate-800 flex items-center justify-center">
            <Users className="w-8 h-8 text-slate-600" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-300">No doctors found</h3>
            <p className="text-sm text-slate-500 mt-1">Try adjusting your filters or search terms.</p>
          </div>
          <button
            onClick={() => { setSearch(''); setFilters(f => ({ ...f, specialization: 'all', city: 'all', availability: 'all' })); }}
            className="px-4 py-2 text-sm font-semibold text-blue-400 bg-blue-500/10 rounded-xl border border-blue-500/20 hover:bg-blue-500/20 transition-colors"
          >
            Clear all filters
          </button>
        </div>
      )}

      {/* Grouped Doctor List */}
      {!loading && Object.entries(grouped).map(([city, cityDoctors]) => (
        <div key={city} className="space-y-3">
          <div className="flex items-center gap-3">
            <h2 className="text-xs font-bold uppercase tracking-widest text-slate-500">{city}</h2>
            <div className="flex-1 h-px bg-white/5" />
            <span className="text-xs text-slate-600">{cityDoctors.length} {cityDoctors.length === 1 ? 'doctor' : 'doctors'}</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {cityDoctors.map((doc, i) => (
              <DoctorCard
                key={doc.id}
                doctor={doc}
                index={i}
                onSelect={onSelect}
                onViewProfile={onViewProfile}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
