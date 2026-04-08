"use client";
import { useState, useCallback, useEffect } from 'react';
import { supabase } from '@/lib/supabaseClient';
import { Doctor } from '../types/doctor';
import { fetchDoctors, MOCK_DOCTORS } from '../services/doctorsApi';

export type FilterState = {
  specialization: string;
  city: string;
  availability: 'all' | 'online' | 'offline';
  sortBy: 'rating' | 'nearest' | 'soonest';
};

export function useDoctors() {
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState<FilterState>({
    specialization: 'all',
    city: 'all',
    availability: 'all',
    sortBy: 'rating',
  });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchDoctors();
      setDoctors(data);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const channel = supabase.channel('realtime:doctors')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'doctors' }, () => {
        load();
      })
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [load]);

  const filtered = doctors
    .filter(d => {
      if (filters.specialization !== 'all' && d.specialization !== filters.specialization) return false;
      if (filters.city !== 'all' && d.city !== filters.city) return false;
      if (filters.availability === 'online' && !d.onlineAvailable) return false;
      if (filters.availability === 'offline' && !d.offlineAvailable) return false;
      return true;
    })
    .sort((a, b) => {
      if (filters.sortBy === 'rating') return b.avgRating - a.avgRating;
      if (filters.sortBy === 'soonest') return new Date(a.nextAvailable).getTime() - new Date(b.nextAvailable).getTime();
      return a.city.localeCompare(b.city);
    });

  const specializations = ['all', ...Array.from(new Set(MOCK_DOCTORS.map(d => d.specialization)))];
  const cities = ['all', ...Array.from(new Set(MOCK_DOCTORS.map(d => d.city)))];

  return { doctors: filtered, loading, load, filters, setFilters, specializations, cities };
}
