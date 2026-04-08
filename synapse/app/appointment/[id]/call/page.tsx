"use client";

import React, { useState } from 'react';
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
import { VideoCallInterface } from "@/features/appointments/components/VideoCallInterface";
import { getStoredAppointments } from "@/features/appointments/services/bookingApi";
import { Star, Download, RotateCcw } from 'lucide-react';

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function VideoCallPage({ params }: PageProps) {
  const unwrappedParams = React.use(params);
  const [callEnded, setCallEnded] = useState(false);
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);

  // Find appointment from storage
  const appointments = typeof window !== 'undefined' ? getStoredAppointments() : [];
  const appointment = appointments.find(a => a.id === unwrappedParams.id);

  const sharedFiles = appointment?.attachedFiles.map(f => ({
    name: f.name,
    type: f.type as 'xray' | 'report',
  })) || [
    { name: 'AI Diagnostic Report.pdf', type: 'report' as const },
  ];

  if (callEnded) {
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
                <BreadcrumbItem><BreadcrumbPage>Call Ended</BreadcrumbPage></BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </header>
          <main className="flex-1 flex items-center justify-center p-6">
            <div className="max-w-md w-full space-y-6 text-center">
              <div className="w-20 h-20 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto border border-emerald-500/30">
                <span className="text-4xl">📞</span>
              </div>
              <div>
                <h2 className="text-2xl font-black text-slate-100">Call Complete</h2>
                <p className="text-slate-400 mt-1">Thank you for your consultation with {appointment?.doctorName || 'the doctor'}.</p>
              </div>

              <div className="bg-slate-900/60 rounded-2xl border border-white/5 p-6 space-y-4">
                <h3 className="text-sm font-bold text-slate-300">Rate your experience</h3>
                <div className="flex items-center justify-center gap-2">
                  {[1, 2, 3, 4, 5].map(star => (
                    <button
                      key={star}
                      onClick={() => setRating(star)}
                      onMouseEnter={() => setHoverRating(star)}
                      onMouseLeave={() => setHoverRating(0)}
                    >
                      <svg
                        className={`w-8 h-8 transition-colors ${star <= (hoverRating || rating) ? 'text-yellow-400' : 'text-slate-600'}`}
                        fill="currentColor" viewBox="0 0 20 20"
                      >
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                    </button>
                  ))}
                </div>
                {rating > 0 && <p className="text-sm text-emerald-400 font-semibold">Thank you for your {rating}-star rating!</p>}
              </div>

              <div className="grid grid-cols-2 gap-3">
                <button className="flex items-center justify-center gap-2 py-3 px-4 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold rounded-xl border border-white/5 transition-colors text-sm">
                  <Download className="w-4 h-4 text-blue-400" />
                  Download Report
                </button>
                <a
                  href="/dashboard/doctors"
                  className="flex items-center justify-center gap-2 py-3 px-4 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl transition-colors text-sm"
                >
                  <RotateCcw className="w-4 h-4" />
                  Book Again
                </a>
              </div>
            </div>
          </main>
        </SidebarInset>
      </SidebarProvider>
    );
  }

  return (
    <VideoCallInterface
      doctorName={appointment?.doctorName || 'Dr. Specialist'}
      doctorSpecialization={appointment?.doctorSpecialization || 'Specialist'}
      doctorPhoto={`https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=200&h=200&fit=crop&crop=face`}
      sharedFiles={sharedFiles}
      onEndCall={() => setCallEnded(true)}
    />
  );
}
