"use client";

import React, { useState, useEffect } from 'react';
import { AppSidebar } from "@/components/app-sidebar";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { DoctorList } from "@/features/appointments/components/DoctorList";
import { DoctorMapView } from "@/features/appointments/components/DoctorMapView";
import { BookingFlow } from "@/features/appointments/components/BookingFlow";
import { useDoctors } from "@/features/appointments/hooks/useDoctors";
import { useGeolocation } from "@/features/appointments/hooks/useGeolocation";
import { Doctor } from "@/features/appointments/types/doctor";
import { Stethoscope, List, Map as MapIcon } from 'lucide-react';
import { AnimatePresence } from 'framer-motion';

export default function DoctorsPage() {
  const [viewMode, setViewMode] = useState<'list' | 'map'>('list');
  const [bookingDoctor, setBookingDoctor] = useState<Doctor | null>(null);
  const [showBookingFlow, setShowBookingFlow] = useState(false);
  const { doctors, loading, load } = useDoctors();
  const { coords } = useGeolocation();

  useEffect(() => { load(); }, [load]);

  const handleSelect = (doc: Doctor) => {
    setBookingDoctor(doc);
    setShowBookingFlow(true);
  };

  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset className="bg-slate-950 text-slate-50">
        <header className="flex h-16 shrink-0 items-center gap-2 border-b border-white/5 px-4">
          <SidebarTrigger className="-ml-1" />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem>
                <BreadcrumbLink href="/dashboard">Dashboard</BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator />
              <BreadcrumbItem>
                <BreadcrumbPage>Find Doctors</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
        </header>

        <main className="flex-1 overflow-y-auto p-6">
          <div className="mx-auto max-w-6xl space-y-8">
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between md:items-end gap-6">
              <div className="space-y-2">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-blue-500/20 flex items-center justify-center">
                    <Stethoscope className="w-5 h-5 text-blue-400" />
                  </div>
                  <h1 className="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-blue-400 via-emerald-300 to-cyan-400 bg-clip-text text-transparent">
                    Find a Doctor
                  </h1>
                </div>
                <p className="text-slate-400">
                  Verified specialist doctors available for online and in-person consultations.
                </p>
              </div>

              {/* View Toggle */}
              <div className="flex bg-slate-900/80 border border-white/5 rounded-xl p-1 gap-1">
                <button
                  onClick={() => setViewMode('list')}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${viewMode === 'list' ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-400 hover:text-slate-200'}`}
                >
                  <List className="w-4 h-4" /> List View
                </button>
                <button
                  onClick={() => setViewMode('map')}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${viewMode === 'map' ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-400 hover:text-slate-200'}`}
                >
                  <MapIcon className="w-4 h-4" /> Map View
                </button>
              </div>
            </div>

            {/* Content */}
            {viewMode === 'list' ? (
              <DoctorList
                onSelect={handleSelect}
                onViewProfile={handleSelect}
              />
            ) : (
              <DoctorMapView
                doctors={doctors}
                onSelect={handleSelect}
                userLat={coords?.lat}
                userLng={coords?.lng}
              />
            )}
          </div>
        </main>
      </SidebarInset>

      {/* Booking Modal */}
      <AnimatePresence>
        {showBookingFlow && (
          <BookingFlow
            aiReport=""
            scanType="General Consultation"
            uploadedFileName=""
            onClose={() => { setShowBookingFlow(false); setBookingDoctor(null); }}
          />
        )}
      </AnimatePresence>
    </SidebarProvider>
  );
}
