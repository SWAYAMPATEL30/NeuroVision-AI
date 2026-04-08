"use client";

import { useState, useEffect } from "react";
import { AppSidebar } from "@/components/app-sidebar";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbList,
  BreadcrumbPage,
} from "@/components/ui/breadcrumb";
import { Separator } from "@/components/ui/separator";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, Calendar, FileText, Video, Brain, ActivitySquare } from "lucide-react";
import { getStoredAppointments } from "@/features/appointments/services/bookingApi";

export default function Page() {
  const [appointments, setAppointments] = useState<any[]>([]);

  useEffect(() => {
    setAppointments(getStoredAppointments());
  }, []);

  const upcomingAppts = appointments.filter(
    (a) => a.status === "scheduled" && new Date(a.date) >= new Date()
  ).sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset className="bg-slate-950 text-slate-50">
        <header className="flex h-16 shrink-0 items-center gap-2 border-b border-white/5 transition-[width,height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-12 px-4">
          <SidebarTrigger className="-ml-1 text-slate-400 hover:text-slate-100" />
          <Separator orientation="vertical" className="mr-2 h-4 bg-white/10" />
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem>
                <BreadcrumbPage className="text-slate-200 font-semibold">Overview</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
        </header>

        <div className="flex flex-1 flex-col gap-6 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-black text-slate-100 tracking-tight">Dashboard Overview</h1>
              <p className="text-slate-400 mt-1">Welcome back. Here's what's happening with your health today.</p>
            </div>
            <div className="flex gap-2">
              <span className="inline-flex items-center gap-1.5 py-1 px-3 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full text-sm font-medium">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                SYSTEM ONLINE
              </span>
            </div>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <Card className="bg-slate-900 border-white/5">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-slate-400">Total Appointments</CardTitle>
                <Calendar className="h-4 w-4 text-blue-400" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-slate-100">{appointments.length}</div>
                <p className="text-xs text-slate-500">+1 from last month</p>
              </CardContent>
            </Card>
            <Card className="bg-slate-900 border-white/5">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-slate-400">AI Diagnostics</CardTitle>
                <Brain className="h-4 w-4 text-purple-400" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-slate-100">3</div>
                <p className="text-xs text-slate-500">Scans Analyzed</p>
              </CardContent>
            </Card>
            <Card className="bg-slate-900 border-white/5">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-slate-400">Upcoming Video Calls</CardTitle>
                <Video className="h-4 w-4 text-emerald-400" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-slate-100">{upcomingAppts.filter(a => a.type === 'video').length}</div>
                <p className="text-xs text-slate-500">Requires attendance</p>
              </CardContent>
            </Card>
            <Card className="bg-slate-900 border-white/5">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-slate-400">Health Reports</CardTitle>
                <FileText className="h-4 w-4 text-amber-400" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-slate-100">12</div>
                <p className="text-xs text-slate-500">Available to download</p>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-6 md:grid-cols-7 lg:grid-cols-7">
            <Card className="bg-slate-900 border-white/5 xl:col-span-4 md:col-span-7 col-span-7">
              <CardHeader>
                <CardTitle className="text-slate-100">Upcoming Sessions</CardTitle>
              </CardHeader>
              <CardContent>
                {upcomingAppts.length === 0 ? (
                  <div className="text-center py-8">
                    <p className="text-slate-400 mb-4">No upcoming appointments scheduled.</p>
                    <a href="/dashboard/doctors" className="inline-flex items-center gap-2 py-2 px-4 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-lg transition-colors">
                      <Calendar className="w-4 h-4" />
                      Book Now
                    </a>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {upcomingAppts.slice(0, 3).map((appt) => (
                      <div key={appt.id} className="flex items-center justify-between p-4 rounded-xl bg-slate-950/50 border border-white/5">
                        <div className="flex items-center gap-4">
                          <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center shrink-0 border border-white/10">
                            {appt.type === 'video' ? <Video className="w-5 h-5 text-blue-400" /> : <ActivitySquare className="w-5 h-5 text-emerald-400" />}
                          </div>
                          <div>
                            <p className="font-semibold text-slate-200">{appt.doctorName}</p>
                            <p className="text-sm text-slate-400">{new Date(appt.date).toLocaleDateString()} at {appt.time}</p>
                          </div>
                        </div>
                        {appt.type === 'video' && (
                          <a href={`/appointment/${appt.id}/call`} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-semibold transition-colors shadow-lg shadow-blue-900/20">
                            Join Call
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="bg-slate-900 border-white/5 xl:col-span-3 md:col-span-7 col-span-7">
              <CardHeader>
                <CardTitle className="text-slate-100">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <a href="/dashboard/neurovision" className="w-full flex items-center gap-3 p-4 rounded-xl bg-slate-950 hover:bg-slate-800 border border-white/5 transition-colors group">
                  <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center group-hover:bg-purple-500/20 transition-colors">
                    <Brain className="w-5 h-5 text-purple-400" />
                  </div>
                  <div className="flex-1 text-left line-clamp-1">
                    <p className="font-semibold text-slate-200">Start AI Diagnosis</p>
                    <p className="text-xs text-slate-400">Analyze MRI or X-Rays</p>
                  </div>
                </a>
                <a href="/dashboard/voice" className="w-full flex items-center gap-3 p-4 rounded-xl bg-slate-950 hover:bg-slate-800 border border-white/5 transition-colors group">
                  <div className="w-10 h-10 rounded-lg bg-pink-500/10 flex items-center justify-center group-hover:bg-pink-500/20 transition-colors">
                    <Activity className="w-5 h-5 text-pink-400" />
                  </div>
                  <div className="flex-1 text-left line-clamp-1">
                    <p className="font-semibold text-slate-200">Voice Therapist</p>
                    <p className="text-xs text-slate-400">Talk to Aria (AI Therapist)</p>
                  </div>
                </a>
                <a href="/dashboard/doctors" className="w-full flex items-center gap-3 p-4 rounded-xl bg-slate-950 hover:bg-slate-800 border border-white/5 transition-colors group">
                  <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center group-hover:bg-emerald-500/20 transition-colors">
                    <Calendar className="w-5 h-5 text-emerald-400" />
                  </div>
                  <div className="flex-1 text-left line-clamp-1">
                    <p className="font-semibold text-slate-200">Find a Specialist</p>
                    <p className="text-xs text-slate-400">Book clinical appointments</p>
                  </div>
                </a>
              </CardContent>
            </Card>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}

