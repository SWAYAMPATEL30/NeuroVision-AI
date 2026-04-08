import pathlib

SYNAPSE = pathlib.Path(r"c:\Users\ipate\OneDrive\Documents\try\synapse")

# ---- SLOT BOOKING PAGE ----
booking_dir = SYNAPSE / "app" / "dashboard" / "book-appointment"
booking_dir.mkdir(parents=True, exist_ok=True)

booking_page = r'''
"use client";

import React, { useState, useEffect, useCallback } from "react";
import { AppSidebar } from "@/components/app-sidebar";
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from "@/components/ui/breadcrumb";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { CalendarDays, Clock, CheckCircle2, User, Phone, FileText, ChevronRight, ChevronLeft, Stethoscope } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const BOOKING_KEY = "synapse-all-bookings";

const DOCTORS = [
  { id: "D1", name: "Dr. Priya Sharma", specialty: "Cardiologist", location: "Mumbai" },
  { id: "D2", name: "Dr. Rahul Mehta", specialty: "Neurologist", location: "Delhi" },
  { id: "D3", name: "Dr. Anjali Singh", specialty: "Pulmonologist", location: "Bangalore" },
  { id: "D4", name: "Dr. Vikram Patel", specialty: "Orthopedic Surgeon", location: "Pune" },
  { id: "D5", name: "Dr. Sneha Rao", specialty: "Psychiatrist", location: "Hyderabad" },
];

const TIME_SLOTS = [
  "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM",
  "11:00 AM", "11:30 AM", "02:00 PM", "02:30 PM",
  "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM",
];

interface Booking {
  id: string;
  doctorId: string;
  doctorName: string;
  patientName: string;
  phone: string;
  reason: string;
  date: string;
  time: string;
  type: string;
  status: string;
  createdAt: string;
}

function getBookedSlots(doctorId: string, date: string): string[] {
  try {
    const stored = localStorage.getItem(BOOKING_KEY);
    if (!stored) return [];
    const all: Booking[] = JSON.parse(stored);
    return all.filter(b => b.doctorId === doctorId && b.date === date && b.status !== "cancelled").map(b => b.time);
  } catch { return []; }
}

function saveBooking(booking: Booking) {
  try {
    const stored = localStorage.getItem(BOOKING_KEY);
    const all: Booking[] = stored ? JSON.parse(stored) : [];
    all.push(booking);
    localStorage.setItem(BOOKING_KEY, JSON.stringify(all));
    // Notify doctor dashboard via BroadcastChannel (free, browser-native)
    if (typeof BroadcastChannel !== "undefined") {
      const bc = new BroadcastChannel("synapse-bookings");
      bc.postMessage({ type: "new-booking", booking });
      bc.close();
    }
  } catch {}
}

export default function BookAppointmentPage() {
  const [step, setStep] = useState(1);
  const [selectedDoctor, setSelectedDoctor] = useState<typeof DOCTORS[0] | null>(null);
  const [selectedDate, setSelectedDate] = useState("");
  const [selectedTime, setSelectedTime] = useState("");
  const [consultType, setConsultType] = useState("video");
  const [bookedSlots, setBookedSlots] = useState<string[]>([]);
  const [patientName, setPatientName] = useState("");
  const [phone, setPhone] = useState("");
  const [reason, setReason] = useState("");
  const [confirmation, setConfirmation] = useState<Booking | null>(null);

  // Get today minimum date
  const today = new Date().toISOString().split("T")[0];

  useEffect(() => {
    if (selectedDoctor && selectedDate) {
      setBookedSlots(getBookedSlots(selectedDoctor.id, selectedDate));
    }
  }, [selectedDoctor, selectedDate]);

  const handleConfirm = () => {
    if (!selectedDoctor || !selectedDate || !selectedTime || !patientName.trim() || !phone.trim()) return;
    const booking: Booking = {
      id: crypto.randomUUID(),
      doctorId: selectedDoctor.id,
      doctorName: selectedDoctor.name,
      patientName: patientName.trim(),
      phone: phone.trim(),
      reason: reason.trim(),
      date: selectedDate,
      time: selectedTime,
      type: consultType,
      status: "confirmed",
      createdAt: new Date().toISOString(),
    };
    saveBooking(booking);
    setConfirmation(booking);
    setStep(5);
  };

  const reset = () => {
    setStep(1); setSelectedDoctor(null); setSelectedDate(""); setSelectedTime("");
    setPatientName(""); setPhone(""); setReason(""); setConfirmation(null);
  };

  const canProceed = () => {
    if (step === 1) return !!selectedDoctor;
    if (step === 2) return !!selectedDate && !!selectedTime;
    if (step === 3) return !!consultType;
    if (step === 4) return !!patientName.trim() && !!phone.trim();
    return false;
  };

  const stepLabels = ["Doctor", "Date & Time", "Type", "Details", "Done"];

  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
          <SidebarTrigger />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem><BreadcrumbLink href="/dashboard">Dashboard</BreadcrumbLink></BreadcrumbItem>
              <BreadcrumbSeparator />
              <BreadcrumbItem><BreadcrumbPage>Book Appointment</BreadcrumbPage></BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
        </header>

        <main className="p-6 max-w-2xl mx-auto w-full">
          <div className="mb-8 space-y-2">
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <CalendarDays className="w-8 h-8 text-primary" /> Book Appointment
            </h1>
            <p className="text-muted-foreground">Secure your slot in 4 simple steps</p>
          </div>

          {/* Progress indicator */}
          <div className="flex items-center mb-8">
            {stepLabels.map((label, i) => (
              <React.Fragment key={label}>
                <div className="flex flex-col items-center">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold border-2 transition-all ${
                    step > i + 1 ? "bg-primary border-primary text-primary-foreground" :
                    step === i + 1 ? "border-primary text-primary" :
                    "border-muted-foreground/30 text-muted-foreground/30"
                  }`}>
                    {step > i + 1 ? <CheckCircle2 className="w-4 h-4" /> : i + 1}
                  </div>
                  <span className={`text-xs mt-1 hidden sm:block ${step === i + 1 ? "text-primary font-medium" : "text-muted-foreground/50"}`}>
                    {label}
                  </span>
                </div>
                {i < stepLabels.length - 1 && (
                  <div className={`flex-1 h-0.5 mx-2 ${step > i + 1 ? "bg-primary" : "bg-muted-foreground/20"}`} />
                )}
              </React.Fragment>
            ))}
          </div>

          <AnimatePresence mode="wait">
            <motion.div
              key={step}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
            >
              {/* Step 1: Doctor Selection */}
              {step === 1 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2"><Stethoscope className="w-5 h-5 text-primary" /> Select a Doctor</CardTitle>
                    <CardDescription>Choose from our verified specialists</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {DOCTORS.map(doc => (
                      <button
                        key={doc.id}
                        onClick={() => setSelectedDoctor(doc)}
                        className={`w-full p-4 rounded-xl border-2 text-left transition-all hover:border-primary/60 hover:bg-primary/5 ${
                          selectedDoctor?.id === doc.id ? "border-primary bg-primary/10" : "border-border"
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                            <Stethoscope className="w-5 h-5 text-primary" />
                          </div>
                          <div>
                            <p className="font-semibold">{doc.name}</p>
                            <p className="text-sm text-muted-foreground">{doc.specialty} • {doc.location}</p>
                          </div>
                          {selectedDoctor?.id === doc.id && <CheckCircle2 className="w-5 h-5 text-primary ml-auto" />}
                        </div>
                      </button>
                    ))}
                  </CardContent>
                </Card>
              )}

              {/* Step 2: Date & Time */}
              {step === 2 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2"><CalendarDays className="w-5 h-5 text-primary" /> Pick Date & Time</CardTitle>
                    <CardDescription>Select an available slot with {selectedDoctor?.name}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div>
                      <Label htmlFor="date" className="mb-2 block">Appointment Date</Label>
                      <Input
                        id="date"
                        type="date"
                        min={today}
                        value={selectedDate}
                        onChange={e => { setSelectedDate(e.target.value); setSelectedTime(""); }}
                        className="max-w-xs"
                      />
                    </div>
                    {selectedDate && (
                      <div>
                        <Label className="mb-3 block flex items-center gap-2">
                          <Clock className="w-4 h-4" /> Available Time Slots
                          <span className="text-xs text-muted-foreground ml-1">({bookedSlots.length} booked)</span>
                        </Label>
                        <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
                          {TIME_SLOTS.map(slot => {
                            const isBooked = bookedSlots.includes(slot);
                            return (
                              <button
                                key={slot}
                                onClick={() => !isBooked && setSelectedTime(slot)}
                                disabled={isBooked}
                                className={`py-2 px-3 rounded-lg text-sm font-medium border-2 transition-all ${
                                  isBooked ? "border-muted bg-muted/30 text-muted-foreground/40 line-through cursor-not-allowed" :
                                  selectedTime === slot ? "border-primary bg-primary text-primary-foreground" :
                                  "border-border hover:border-primary/60 hover:bg-primary/5"
                                }`}
                              >
                                {slot}
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {/* Step 3: Consult Type */}
              {step === 3 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Consultation Type</CardTitle>
                    <CardDescription>How would you like to meet {selectedDoctor?.name}?</CardDescription>
                  </CardHeader>
                  <CardContent className="grid grid-cols-2 gap-4">
                    {[
                      { id: "video", label: "Video Consult", desc: "Meet online via secure video call" },
                      { id: "in-person", label: "In-Person", desc: "Visit the clinic at scheduled time" },
                    ].map(opt => (
                      <button
                        key={opt.id}
                        onClick={() => setConsultType(opt.id)}
                        className={`p-6 rounded-2xl border-2 text-center transition-all ${
                          consultType === opt.id ? "border-primary bg-primary/10" : "border-border hover:border-primary/40"
                        }`}
                      >
                        <p className="font-bold text-lg">{opt.label}</p>
                        <p className="text-sm text-muted-foreground mt-1">{opt.desc}</p>
                        {consultType === opt.id && <CheckCircle2 className="w-5 h-5 text-primary mx-auto mt-3" />}
                      </button>
                    ))}
                  </CardContent>
                </Card>
              )}

              {/* Step 4: Patient Details */}
              {step === 4 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2"><User className="w-5 h-5 text-primary" /> Your Details</CardTitle>
                    <CardDescription>Confirm your information for the booking</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="name">Full Name *</Label>
                      <div className="relative">
                        <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                        <Input id="name" placeholder="Enter your full name" className="pl-10" value={patientName} onChange={e => setPatientName(e.target.value)} />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="phone">Phone Number *</Label>
                      <div className="relative">
                        <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                        <Input id="phone" placeholder="+91 XXXXXXXXXX" className="pl-10" value={phone} onChange={e => setPhone(e.target.value)} />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="reason">Reason for Visit</Label>
                      <div className="relative">
                        <FileText className="absolute left-3 top-3 w-4 h-4 text-muted-foreground" />
                        <textarea  
                          id="reason"
                          placeholder="Brief description of your concern..."
                          className="w-full pl-10 pr-4 py-2 rounded-md border border-input bg-background text-sm resize-none h-24 focus:outline-none focus:ring-2 focus:ring-ring"
                          value={reason}
                          onChange={e => setReason(e.target.value)}
                        />
                      </div>
                    </div>
                    <div className="bg-muted/30 rounded-xl p-4 text-sm space-y-1 border">
                      <p className="font-semibold mb-2">Booking Summary</p>
                      <p><span className="text-muted-foreground">Doctor:</span> {selectedDoctor?.name} ({selectedDoctor?.specialty})</p>
                      <p><span className="text-muted-foreground">Date:</span> {selectedDate}</p>
                      <p><span className="text-muted-foreground">Time:</span> {selectedTime}</p>
                      <p><span className="text-muted-foreground">Type:</span> {consultType === "video" ? "Video Consult" : "In-Person"}</p>
                    </div>
                  </CardContent>
                  <CardFooter>
                    <Button onClick={handleConfirm} disabled={!canProceed()} className="w-full">
                      <CheckCircle2 className="w-4 h-4 mr-2" /> Confirm Booking
                    </Button>
                  </CardFooter>
                </Card>
              )}

              {/* Step 5: Confirmation */}
              {step === 5 && confirmation && (
                <Card className="border-green-500/30 bg-green-500/5">
                  <CardContent className="p-8 text-center space-y-6">
                    <div className="w-20 h-20 rounded-full bg-green-500/20 border-2 border-green-500/40 flex items-center justify-center mx-auto">
                      <CheckCircle2 className="w-10 h-10 text-green-500" />
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-green-600 dark:text-green-400">Booking Confirmed!</h2>
                      <p className="text-muted-foreground mt-1">Your appointment has been booked successfully.</p>
                    </div>
                    <div className="bg-background rounded-xl p-4 text-left space-y-2 border text-sm">
                      <p><span className="text-muted-foreground">Booking ID:</span> <span className="font-mono font-bold text-primary">{confirmation.id.slice(0, 8).toUpperCase()}</span></p>
                      <p><span className="text-muted-foreground">Doctor:</span> {confirmation.doctorName}</p>
                      <p><span className="text-muted-foreground">Patient:</span> {confirmation.patientName}</p>
                      <p><span className="text-muted-foreground">Date & Time:</span> {confirmation.date} at {confirmation.time}</p>
                      <p><span className="text-muted-foreground">Type:</span> {confirmation.type === "video" ? "Video Consult" : "In-Person"}</p>
                    </div>
                    <Button onClick={reset} variant="outline" className="w-full">Book Another Appointment</Button>
                  </CardContent>
                </Card>
              )}
            </motion.div>
          </AnimatePresence>

          {/* Navigation */}
          {step < 5 && (
            <div className="flex justify-between mt-6">
              <Button variant="outline" onClick={() => setStep(s => Math.max(1, s - 1))} disabled={step === 1}>
                <ChevronLeft className="w-4 h-4 mr-1" /> Back
              </Button>
              {step < 4 && (
                <Button onClick={() => setStep(s => s + 1)} disabled={!canProceed()}>
                  Next <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
              )}
            </div>
          )}
        </main>
      </SidebarInset>
    </SidebarProvider>
  );
}
'''.strip()
(booking_dir / "page.tsx").write_text(booking_page, encoding="utf-8")
print("Booking page written!")
