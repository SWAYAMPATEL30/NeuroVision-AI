"use client";
import React, { useState, useEffect } from "react";
import { AppSidebar } from "@/components/app-sidebar";
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from "@/components/ui/breadcrumb";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { CalendarDays, Clock, Video, MapPin, CheckCircle2, XCircle } from "lucide-react";

const BOOKING_KEY = "synapse-all-bookings";

interface Booking {
  id: string;
  patientName: string;
  date: string;
  time: string;
  type?: string;
  reason?: string;
  status: string;
}

export default function DoctorAppointmentsPage() {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    try {
      const stored = localStorage.getItem(BOOKING_KEY);
      if (stored) setBookings(JSON.parse(stored));
    } catch {}
    // BroadcastChannel: real-time updates across tabs
    const bc = typeof BroadcastChannel !== "undefined" ? new BroadcastChannel("synapse-bookings") : null;
    if (bc) {
      bc.onmessage = () => {
        try {
          const s = localStorage.getItem(BOOKING_KEY);
          if (s) setBookings(JSON.parse(s));
        } catch {}
      };
    }
    return () => bc?.close();
  }, []);

  const filtered = filter === "all" ? bookings : bookings.filter(b => b.status.toLowerCase() === filter);

  const updateStatus = (id: string, status: string) => {
    const updated = bookings.map(b => b.id === id ? { ...b, status } : b);
    setBookings(updated);
    try { localStorage.setItem(BOOKING_KEY, JSON.stringify(updated)); } catch {}
  };

  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
          <SidebarTrigger />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem><BreadcrumbLink href="/doctor/dashboard">Doctor Portal</BreadcrumbLink></BreadcrumbItem>
              <BreadcrumbSeparator />
              <BreadcrumbItem><BreadcrumbPage>Appointments</BreadcrumbPage></BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
        </header>
        <main className="p-6 space-y-6">
          <div className="flex flex-col md:flex-row justify-between md:items-center gap-4">
            <div>
              <h1 className="text-3xl font-bold flex items-center gap-2"><CalendarDays className="w-7 h-7 text-primary" /> Appointments</h1>
              <p className="text-muted-foreground mt-1">Real-time booking updates via BroadcastChannel</p>
            </div>
            <div className="flex gap-2">
              {["all", "confirmed", "pending", "cancelled"].map(f => (
                <Button key={f} variant={filter === f ? "default" : "outline"} size="sm" onClick={() => setFilter(f)} className="capitalize">{f}</Button>
              ))}
            </div>
          </div>
          {filtered.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center text-muted-foreground">
                <CalendarDays className="w-12 h-12 mx-auto mb-4 opacity-30" />
                <p>No appointments found. New bookings will appear here in real-time.</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              {filtered.map(b => (
                <Card key={b.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="flex items-start gap-4">
                      <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center shrink-0">
                        <CalendarDays className="w-5 h-5 text-primary" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-lg">{b.patientName}</h3>
                        <div className="flex items-center flex-wrap gap-3 text-sm text-muted-foreground mt-1">
                          <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{b.date} at {b.time}</span>
                          <span className="flex items-center gap-1">{b.type === "video" ? <Video className="w-3 h-3" /> : <MapPin className="w-3 h-3" />}{b.type || "In-Person"}</span>
                          {b.reason && <span>Reason: {b.reason}</span>}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 self-end md:self-auto">
                      <Badge variant="outline" className="capitalize">{b.status}</Badge>
                      {b.status !== "confirmed" && (
                        <Button size="sm" variant="default" onClick={() => updateStatus(b.id, "confirmed")} className="gap-1">
                          <CheckCircle2 className="w-3 h-3" /> Confirm
                        </Button>
                      )}
                      {b.status !== "cancelled" && (
                        <Button size="sm" variant="destructive" onClick={() => updateStatus(b.id, "cancelled")} className="gap-1">
                          <XCircle className="w-3 h-3" /> Cancel
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </main>
      </SidebarInset>
    </SidebarProvider>
  );
}