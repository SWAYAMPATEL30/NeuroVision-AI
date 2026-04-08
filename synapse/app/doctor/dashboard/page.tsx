"use client";

import React, { useState, useEffect, useCallback } from "react";
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
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { CalendarDays, Users, Activity, Clock, ChevronRight, FileText, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "@/lib/auth";
import { getDoctorAppointments } from "@/features/appointments/services/bookingApi";
import { Appointment } from "@/features/appointments/types/appointment";
import { supabase } from "@/lib/supabaseClient";

export default function DoctorDashboard() {
  const { user } = useAuth();
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const doctorName = user?.name || "Doctor";

  const fetchAppointments = useCallback(async () => {
    if (!user?.id) return;
    const data = await getDoctorAppointments(user.id);
    setAppointments(data);
    setLoading(false);
  }, [user?.id]);

  useEffect(() => {
    fetchAppointments();

    const channel = supabase
      .channel('doctor-appointments')
      .on('postgres_changes', 
        { event: '*', schema: 'public', table: 'appointments', filter: `doctorId=eq.${user?.id}` }, 
        () => {
          fetchAppointments();
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [user?.id, fetchAppointments]);


  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center justify-between gap-2 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 px-4">
          <div className="flex items-center gap-2">
            <SidebarTrigger className="-ml-1" />
            <Separator orientation="vertical" className="mr-2 data-[orientation=vertical]:h-4" />
            <Breadcrumb>
              <BreadcrumbList>
                <BreadcrumbItem className="hidden md:block">
                  <BreadcrumbLink href="/doctor/dashboard">Doctor Workspace</BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator className="hidden md:block" />
                <BreadcrumbItem>
                  <BreadcrumbPage>Dashboard</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium text-muted-foreground hidden sm:inline-block">
              Welcome back, {doctorName}
            </span>
            <Avatar className="h-8 w-8 ring-2 ring-primary/20 cursor-pointer hover:ring-primary/60 transition-all">
              <AvatarImage src="https://i.pravatar.cc/150?u=doc1" />
              <AvatarFallback>DR</AvatarFallback>
            </Avatar>
          </div>
        </header>

        <div className="flex-1 overflow-auto bg-muted/20">
          <motion.div 
            className="p-4 md:p-8 max-w-7xl mx-auto space-y-8"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            {/* Overview Stats */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <motion.div variants={itemVariants}>
                <Card className="border-l-4 border-l-primary shadow-sm hover:shadow-md transition-all">
                  <CardContent className="p-6">
                    <div className="flex justify-between items-start">
                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground font-medium">Today's Patients</p>
                        <p className="text-3xl font-bold">12</p>
                      </div>
                      <div className="p-3 bg-primary/10 rounded-full text-primary">
                        <Users className="w-5 h-5" />
                      </div>
                    </div>
                    <div className="mt-4 flex items-center text-sm">
                      <span className="text-green-500 font-medium flex items-center">
                        +2 <span className="ml-1 text-muted-foreground font-normal">from yesterday</span>
                      </span>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              <motion.div variants={itemVariants}>
                <Card className="border-l-4 border-l-orange-500 shadow-sm hover:shadow-md transition-all">
                  <CardContent className="p-6">
                    <div className="flex justify-between items-start">
                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground font-medium">Pending Reports</p>
                        <p className="text-3xl font-bold">5</p>
                      </div>
                      <div className="p-3 bg-orange-500/10 rounded-full text-orange-500">
                        <FileText className="w-5 h-5" />
                      </div>
                    </div>
                    <div className="mt-4 flex items-center text-sm">
                      <span className="text-orange-500 font-medium flex items-center">
                        Requires action
                      </span>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              <motion.div variants={itemVariants}>
                <Card className="border-l-4 border-l-purple-500 shadow-sm hover:shadow-md transition-all">
                  <CardContent className="p-6">
                    <div className="flex justify-between items-start">
                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground font-medium">AI Scans Analyzed</p>
                        <p className="text-3xl font-bold">24</p>
                      </div>
                      <div className="p-3 bg-purple-500/10 rounded-full text-purple-500">
                        <Activity className="w-5 h-5" />
                      </div>
                    </div>
                    <div className="mt-4 flex items-center text-sm">
                      <span className="text-muted-foreground">This week</span>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              <motion.div variants={itemVariants}>
                <Card className="border-l-4 border-l-green-500 shadow-sm hover:shadow-md transition-all">
                  <CardContent className="p-6">
                    <div className="flex justify-between items-start">
                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground font-medium">Hours Consulted</p>
                        <p className="text-3xl font-bold">32.5</p>
                      </div>
                      <div className="p-3 bg-green-500/10 rounded-full text-green-500">
                        <Clock className="w-5 h-5" />
                      </div>
                    </div>
                    <div className="mt-4 flex items-center text-sm">
                      <span className="text-muted-foreground">This week</span>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </div>

            <div className="grid gap-6 md:grid-cols-7">
              {/* Daily Schedule */}
              <motion.div variants={itemVariants} className="md:col-span-4 lg:col-span-4">
                <Card className="h-full flex flex-col shadow-sm">
                  <CardHeader className="border-b bg-muted/10 py-5">
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-xl flex items-center gap-2">
                          <CalendarDays className="w-5 h-5 text-primary" />
                          Today's Appointments
                        </CardTitle>
                        <CardDescription className="mt-1">You have {appointments.length} appointments scheduled.</CardDescription>
                      </div>
                      <Button variant="outline" size="sm" className="hidden sm:flex rounded-full" onClick={fetchAppointments}>
                        Refresh
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent className="flex-1 p-0">
                    <div className="divide-y max-h-[500px] overflow-y-auto">
                      {loading ? (
                        <div className="p-10 text-center space-y-3">
                          <Loader2 className="w-8 h-8 animate-spin mx-auto text-primary" />
                          <p className="text-sm text-muted-foreground">Loading your appointments...</p>
                        </div>
                      ) : appointments.length === 0 ? (
                        <div className="p-10 text-center text-muted-foreground italic">
                          No upcoming appointments found.
                        </div>
                      ) : (
                        appointments.map((apt) => (
                          <div key={apt.id} className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-muted/30 transition-colors">
                            <div className="flex items-center gap-4">
                              <div className="w-16 h-16 rounded-xl bg-primary/10 flex flex-col items-center justify-center text-primary border border-primary/20 shrink-0">
                                <span className="text-lg font-bold leading-none">{apt.time?.split(' ')[0] || "09:00"}</span>
                                <span className="text-xs uppercase font-medium mt-1">{apt.time?.split(' ')[1] || "AM"}</span>
                              </div>
                              <div>
                                <h4 className="font-semibold text-lg">{(apt as any).patientName || "Patient"}</h4>
                                <p className="text-sm text-muted-foreground flex items-center gap-2">
                                  <span className={`inline-block w-2 h-2 rounded-full ${apt.mode === 'online' ? 'bg-blue-500' : 'bg-green-500'}`}></span>
                                  {apt.mode === 'online' ? 'Video Consult' : 'In-Person'} • {apt.scanType || "General"}
                                </p>
                              </div>
                            </div>
                            <div className="flex items-center gap-3 self-end sm:self-auto">
                              <Badge variant={apt.status === "confirmed" ? "secondary" : "outline"} className="px-3 py-1">
                                {apt.status}
                              </Badge>
                              <Button size="sm" variant={apt.mode === 'online' ? "default" : "secondary"}>
                                {apt.mode === 'online' ? "Start Call" : "View Details"}
                              </Button>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Recent AI Scans Queue - Placeholder for future implementation */}
              <motion.div variants={itemVariants} className="md:col-span-3 lg:col-span-3">
                <Card className="h-full flex flex-col shadow-sm">
                  <CardHeader className="border-b bg-muted/10 py-5">
                    <CardTitle className="text-xl flex items-center gap-2">
                      <Activity className="w-5 h-5 text-purple-500" />
                      Platform Status
                    </CardTitle>
                    <CardDescription className="mt-1">AI Diagnostic systems are operational.</CardDescription>
                  </CardHeader>
                  <CardContent className="p-10 text-center">
                    <div className="w-16 h-16 rounded-full bg-green-500/10 flex items-center justify-center mx-auto mb-4 border border-green-500/20">
                      <Activity className="w-8 h-8 text-green-500" />
                    </div>
                    <p className="font-semibold">All Systems Go</p>
                    <p className="text-sm text-muted-foreground mt-2">Real-time scan monitoring is enabled for your clinic.</p>
                  </CardContent>
                </Card>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}
