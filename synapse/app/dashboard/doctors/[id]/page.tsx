"use client";

import React, { useEffect, useState } from 'react';
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
import { fetchDoctorById } from "@/features/appointments/services/doctorsApi";
import { BookingFlow } from "@/features/appointments/components/BookingFlow";
import { Doctor, TimeSlot } from "@/features/appointments/types/doctor";
import { 
  Star, MapPin, Video, Building2, Award, Calendar, 
  ChevronLeft, ArrowRight, CheckCircle 
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '@/lib/auth';

interface PageProps {
  params: { id: string };
}

function StarRating({ rating }: { rating: number }) {
  return (
    <div className="flex items-center gap-1">
      {[1, 2, 3, 4, 5].map(star => (
        <svg key={star} className={`w-4 h-4 ${star <= Math.round(rating) ? 'text-yellow-400' : 'text-slate-600'}`} fill="currentColor" viewBox="0 0 20 20">
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
        </svg>
      ))}
    </div>
  );
}

export default function DoctorProfilePage({ params }: PageProps) {
  const { user } = useAuth();
  const [doctor, setDoctor] = useState<Doctor | null>(null);
  const [loading, setLoading] = useState(true);
  const [showBooking, setShowBooking] = useState(false);
  const [activeTab, setActiveTab] = useState<'about' | 'reviews' | 'slots'>('about');

  useEffect(() => {
    fetchDoctorById(params.id).then(d => {
      setDoctor(d || null);
      setLoading(false);
    });
  }, [params.id]);

  if (loading) {
    return (
      <SidebarProvider>
        <AppSidebar />
        <SidebarInset className="bg-slate-950 text-slate-50">
          <div className="flex items-center justify-center h-full">
            <div className="w-16 h-16 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin" />
          </div>
        </SidebarInset>
      </SidebarProvider>
    );
  }

  if (!doctor) {
    return (
      <SidebarProvider>
        <AppSidebar />
        <SidebarInset className="bg-slate-950 text-slate-50">
          <div className="flex flex-col items-center justify-center h-full gap-4">
            <p className="text-2xl font-bold text-slate-300">Doctor not found</p>
            <a href="/dashboard/doctors" className="text-blue-400 hover:underline">← Back to Doctors</a>
          </div>
        </SidebarInset>
      </SidebarProvider>
    );
  }

  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset className="bg-slate-950 text-slate-50">
        <header className="flex h-16 shrink-0 items-center gap-2 border-b border-white/5 px-4">
          <SidebarTrigger className="-ml-1" />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem><BreadcrumbLink href="/dashboard">Dashboard</BreadcrumbLink></BreadcrumbItem>
              <BreadcrumbSeparator />
              <BreadcrumbItem><BreadcrumbLink href="/dashboard/doctors">Find Doctors</BreadcrumbLink></BreadcrumbItem>
              <BreadcrumbSeparator />
              <BreadcrumbItem><BreadcrumbPage>{doctor.name}</BreadcrumbPage></BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
        </header>

        <main className="flex-1 overflow-y-auto p-6">
          <div className="mx-auto max-w-4xl space-y-8">
            <a href="/dashboard/doctors" className="flex items-center gap-2 text-sm text-slate-400 hover:text-slate-200 transition-colors w-fit">
              <ChevronLeft className="w-4 h-4" />
              Back to Doctors
            </a>

            {/* Hero Card */}
            <div className="bg-slate-900/50 rounded-2xl border border-white/5 overflow-hidden">
              <div className="h-32 bg-gradient-to-r from-blue-600/20 via-cyan-600/10 to-emerald-600/10" />
              <div className="px-8 pb-8 -mt-12">
                <div className="flex flex-col md:flex-row md:items-end gap-6">
                  <img
                    src={doctor.photo}
                    alt={doctor.name}
                    className="w-24 h-24 rounded-2xl border-4 border-slate-900 object-cover shadow-xl"
                    onError={(e) => { (e.target as HTMLImageElement).src = 'https://via.placeholder.com/96x96/1e293b/94a3b8?text=Dr'; }}
                  />
                  <div className="flex-1">
                    <h1 className="text-3xl font-black text-slate-100">{doctor.name}</h1>
                    <p className="text-lg text-blue-400 font-semibold">{doctor.specialization}</p>
                    <p className="text-sm text-slate-400 mt-1">{doctor.degree} · {doctor.university} · {doctor.graduationYear}</p>
                    <div className="flex flex-wrap items-center gap-3 mt-3">
                      <div className="flex items-center gap-2">
                        <StarRating rating={doctor.avgRating} />
                        <span className="text-lg font-black text-yellow-400">{doctor.avgRating}</span>
                        <span className="text-sm text-slate-500">({doctor.reviewCount} reviews)</span>
                      </div>
                      {doctor.onlineAvailable && (
                        <span className="flex items-center gap-1 text-[10px] font-bold uppercase px-2.5 py-1 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30">
                          <Video className="w-3 h-3" /> Online
                        </span>
                      )}
                      {doctor.offlineAvailable && (
                        <span className="flex items-center gap-1 text-[10px] font-bold uppercase px-2.5 py-1 rounded-full bg-slate-700/50 text-slate-400 border border-slate-600/50">
                          <Building2 className="w-3 h-3" /> In-Person
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex flex-col gap-2 md:items-end">
                    <p className="text-xs text-slate-500">Consultation Fee</p>
                    <p className="text-2xl font-black text-slate-100">₹{doctor.consultationFee}</p>
                    <button
                      onClick={() => setShowBooking(true)}
                      className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl transition-all shadow-lg shadow-blue-900/30 text-sm"
                    >
                      Book Appointment <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-3 gap-4 mt-6">
                  {[
                    { label: 'Experience', value: `${doctor.experience}+ Years` },
                    { label: 'Patients Treated', value: `${doctor.reviewCount * 8}+` },
                    { label: 'Reviews', value: `${doctor.reviewCount}` },
                  ].map(stat => (
                    <div key={stat.label} className="bg-slate-800/50 rounded-xl p-4 text-center border border-white/5">
                      <p className="text-xl font-black text-slate-100">{stat.value}</p>
                      <p className="text-[10px] uppercase tracking-widest text-slate-500 mt-1">{stat.label}</p>
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
                  className={`flex-1 py-2.5 text-sm font-semibold rounded-lg transition-all capitalize ${
                    activeTab === tab ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {tab === 'slots' ? 'Available Slots' : tab === 'about' ? 'About & Education' : 'Reviews'}
                </button>
              ))}
            </div>

            {/* Tab Panels */}
            <div className="bg-slate-900/40 rounded-2xl border border-white/5 p-8">
              {activeTab === 'about' && (
                <div className="space-y-6">
                  <div>
                    <h3 className="text-base font-bold text-slate-200 mb-3">About</h3>
                    <p className="text-slate-400 leading-relaxed">{doctor.bio}</p>
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-slate-200 mb-3">Education</h3>
                    <div className="flex items-start gap-3 p-4 bg-slate-800/40 rounded-xl border border-white/5">
                      <Award className="w-5 h-5 text-blue-400 mt-0.5" />
                      <div>
                        <p className="font-semibold text-slate-200">{doctor.degree}</p>
                        <p className="text-sm text-slate-400">{doctor.university} · Class of {doctor.graduationYear}</p>
                      </div>
                    </div>
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-slate-200 mb-3">Certifications</h3>
                    <div className="flex flex-wrap gap-2">
                      {doctor.certifications.map(cert => (
                        <span key={cert} className="flex items-center gap-1.5 text-sm px-3 py-1.5 bg-slate-800 text-slate-300 rounded-full border border-white/5">
                          <CheckCircle className="w-3.5 h-3.5 text-emerald-400" /> {cert}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-slate-200 mb-3">Clinic Location</h3>
                    <div className="flex items-start gap-3 p-4 bg-slate-800/40 rounded-xl border border-white/5">
                      <MapPin className="w-5 h-5 text-slate-400 mt-0.5 flex-shrink-0" />
                      <div>
                        <p className="font-semibold text-slate-200">{doctor.clinicName}</p>
                        <p className="text-sm text-slate-400 mt-0.5">{doctor.address}</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'reviews' && (
                <div className="space-y-5">
                  <div className="flex items-center gap-6 p-4 bg-slate-800/40 rounded-xl border border-white/5">
                    <div className="text-center">
                      <p className="text-5xl font-black text-yellow-400">{doctor.avgRating}</p>
                      <StarRating rating={doctor.avgRating} />
                      <p className="text-xs text-slate-500 mt-1">{doctor.reviewCount} reviews</p>
                    </div>
                    <div className="flex-1 space-y-2">
                      {[5, 4, 3, 2, 1].map(stars => {
                        const count = doctor.reviews.filter(r => r.rating === stars).length;
                        const pct = doctor.reviewCount > 0 ? (count / doctor.reviewCount) * 100 : (stars === 5 ? 70 : stars === 4 ? 20 : 10);
                        return (
                          <div key={stars} className="flex items-center gap-3">
                            <span className="text-xs text-slate-400 w-3">{stars}</span>
                            <svg className="w-3 h-3 text-yellow-400" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" /></svg>
                            <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                              <div className="h-full bg-yellow-400 rounded-full" style={{ width: `${pct}%` }} />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {doctor.reviews.map(review => (
                    <div key={review.id} className="border-b border-white/5 pb-5 last:border-0">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-full bg-blue-500/20 flex items-center justify-center text-sm font-bold text-blue-400">
                            {review.patientName[0]}
                          </div>
                          <div>
                            <p className="font-semibold text-slate-200 text-sm">{review.patientName}</p>
                            <p className="text-xs text-slate-500">{review.date}</p>
                          </div>
                        </div>
                        <StarRating rating={review.rating} />
                      </div>
                      <p className="text-sm text-slate-400 leading-relaxed pl-12">{review.comment}</p>
                    </div>
                  ))}
                </div>
              )}

              {activeTab === 'slots' && (
                <div className="space-y-6">
                  <div className="flex items-center gap-3 p-4 bg-blue-500/10 rounded-xl border border-blue-500/20">
                    <Calendar className="w-5 h-5 text-blue-400" />
                    <div>
                      <p className="text-sm font-semibold text-blue-300">Select a slot below to book</p>
                      <p className="text-xs text-slate-400">All times are in IST. Green slots are available.</p>
                    </div>
                  </div>

                  {Object.entries(
                    doctor.timeSlots.reduce((acc, slot) => {
                      if (!acc[slot.date]) acc[slot.date] = [];
                      acc[slot.date].push(slot);
                      return acc;
                    }, {} as Record<string, TimeSlot[]>)
                  ).map(([date, slots]) => (
                    <div key={date} className="space-y-3">
                      <h4 className="text-xs font-bold uppercase tracking-widest text-slate-500">
                        {new Date(date + 'T00:00:00').toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' })}
                      </h4>
                      <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-2">
                        {slots.map(slot => (
                          <button
                            key={slot.id}
                            disabled={!slot.available}
                            onClick={() => setShowBooking(true)}
                            className={`py-2 px-3 rounded-xl text-xs font-semibold border transition-all ${
                              !slot.available
                                ? 'bg-slate-900/30 border-white/5 text-slate-600 cursor-not-allowed line-through'
                                : 'bg-slate-800/50 border-white/5 text-slate-300 hover:border-blue-500/40 hover:bg-slate-800 hover:text-blue-300'
                            }`}
                          >
                            {slot.time}
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}

                  <button
                    onClick={() => setShowBooking(true)}
                    className="w-full py-4 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl flex items-center justify-center gap-2 transition-colors shadow-lg shadow-blue-900/30"
                  >
                    <Calendar className="w-5 h-5" />
                    Book This Doctor <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          </div>
        </main>
      </SidebarInset>

      <AnimatePresence>
        {showBooking && (
          <BookingFlow
            aiReport=""
            scanType="General Consultation"
            uploadedFileName=""
            patientName={user?.name || "Patient"}
            onClose={() => setShowBooking(false)}
          />
        )}
      </AnimatePresence>
    </SidebarProvider>
  );
}
