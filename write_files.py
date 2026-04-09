import os, pathlib

NeuroVision AI = pathlib.Path(r"c:\Users\ipate\OneDrive\Documents\try\NeuroVision AI")

# ---- 1. CHATBOT PAGE ----
chatbot_dir = NeuroVision AI / "app" / "dashboard" / "chatbot"
chatbot_dir.mkdir(parents=True, exist_ok=True)

chatbot = r'''
"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import { AppSidebar } from "@/components/app-sidebar";
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import {
  Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList,
  BreadcrumbPage, BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Send, Trash2, Bot, Sparkles, Loader2, HeartPulse } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const STORAGE_KEY = "neurovision-chatbot-history";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

const HF_TOKEN = process.env.NEXT_PUBLIC_HF_TOKEN || "";

function getFallbackReply(msg: string): string {
  const m = msg.toLowerCase();
  if (m.includes("headache")) return "Headaches can be caused by tension, dehydration, or migraines. Rest, hydrate, and take OTC pain relief if needed. If severe or persistent, please see a doctor.";
  if (m.includes("fever")) return "Fever often signals infection. Stay hydrated, rest, and use fever reducers if needed. Consult a doctor if it exceeds 103°F or lasts 3+ days.";
  if (m.includes("blood pressure") || m.includes("hypertension")) return "High blood pressure can be managed with less salt, regular exercise, stress management, and prescribed medication. Regular monitoring is key.";
  if (m.includes("diabetes")) return "Diabetes management involves monitoring blood sugar, a healthy diet, regular exercise, and medication adherence. Regular check-ups with your doctor are essential.";
  if (m.includes("chest pain")) return "Chest pain should be taken seriously. If sudden and severe with arm pain or shortness of breath, call emergency services immediately.";
  if (m.includes("hi") || m.includes("hello") || m.includes("hey")) return "Hello! I'm MedBot, your AI medical assistant. I can help you understand symptoms, medications, and health questions. How can I assist you today?";
  return "That's an important health question. I recommend consulting a qualified healthcare professional for proper evaluation. Can you tell me more about your specific concern?";
}

async function callChatAI(userMessage: string, history: Message[]): Promise<string> {
  const contextLines = history
    .slice(-6)
    .map(m => (m.role === "user" ? "User: " : "MedBot: ") + m.content)
    .join("\n");

  const prompt =
    "<|system|>\nYou are MedBot, a medical assistant in NeuroVision AI. Help patients with health questions. " +
    "Always recommend consulting a doctor. Be concise, empathetic, and clear.\n</|system|>\n" +
    (contextLines ? contextLines + "\n" : "") +
    "User: " + userMessage + "\nMedBot:";

  try {
    const res = await fetch(
      "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(HF_TOKEN ? { Authorization: "Bearer " + HF_TOKEN } : {}),
        },
        body: JSON.stringify({
          inputs: prompt,
          parameters: { max_new_tokens: 200, temperature: 0.7, return_full_text: false },
        }),
      }
    );
    if (!res.ok) return getFallbackReply(userMessage);
    const data = await res.json();
    const text: string = data[0]?.generated_text || "";
    const clean = text.split("User:")[0].trim();
    return clean || getFallbackReply(userMessage);
  } catch {
    return getFallbackReply(userMessage);
  }
}

const QUICK_PROMPTS = [
  "What is hypertension?",
  "How to manage stress?",
  "Tips for better sleep",
  "Signs of diabetes",
];

export default function ChatbotPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        setMessages(parsed.map((m: Message) => ({ ...m, timestamp: new Date(m.timestamp) })));
      }
    } catch {}
  }, []);

  useEffect(() => {
    if (messages.length > 0) {
      try { localStorage.setItem(STORAGE_KEY, JSON.stringify(messages)); } catch {}
    }
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || isLoading) return;
    setInput("");
    const userMsg: Message = { id: crypto.randomUUID(), role: "user", content: text.trim(), timestamp: new Date() };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);
    try {
      const reply = await callChatAI(text.trim(), [...messages, userMsg]);
      const botMsg: Message = { id: crypto.randomUUID(), role: "assistant", content: reply, timestamp: new Date() };
      setMessages(prev => [...prev, botMsg]);
    } catch {
      const errMsg: Message = { id: crypto.randomUUID(), role: "assistant", content: "Sorry, I could not process that. Please try again.", timestamp: new Date() };
      setMessages(prev => [...prev, errMsg]);
    } finally {
      setIsLoading(false);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isLoading, messages]);

  const clearHistory = () => {
    setMessages([]);
    localStorage.removeItem(STORAGE_KEY);
  };

  const formatTime = (d: Date) => d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset className="bg-gradient-to-br from-slate-950 via-blue-950/20 to-slate-950 text-slate-50">
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
                <BreadcrumbPage>MedBot AI</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
          <div className="ml-auto flex items-center gap-2">
            <Badge variant="outline" className="border-green-500/30 text-green-400 text-xs gap-1">
              <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
              Online
            </Badge>
            <Button variant="ghost" size="sm" onClick={clearHistory} className="text-slate-400 hover:text-red-400 gap-2">
              <Trash2 className="w-4 h-4" /> Clear
            </Button>
          </div>
        </header>

        <main className="flex-1 overflow-hidden flex flex-col p-4 md:p-6">
          <div className="max-w-3xl mx-auto w-full flex flex-col h-full gap-4">
            {/* Header */}
            <div className="text-center space-y-1 pb-2">
              <div className="flex items-center justify-center gap-3">
                <div className="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
                  <HeartPulse className="w-6 h-6 text-blue-400" />
                </div>
                <div className="text-left">
                  <h1 className="text-2xl font-bold text-white">MedBot AI</h1>
                  <p className="text-xs text-slate-500">Your AI Medical Assistant with Memory</p>
                </div>
              </div>
            </div>

            {/* Chat area */}
            <div className="flex-1 rounded-2xl border border-white/5 bg-slate-900/30 backdrop-blur overflow-hidden flex flex-col">
              <ScrollArea className="flex-1 p-4" ref={scrollRef}>
                {messages.length === 0 ? (
                  <div className="h-full flex flex-col items-center justify-center gap-6 py-10">
                    <div className="w-20 h-20 rounded-full bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
                      <Bot className="w-10 h-10 text-blue-400" />
                    </div>
                    <div className="text-center">
                      <p className="text-lg font-semibold text-slate-300">Hi, I'm MedBot!</p>
                      <p className="text-sm text-slate-500 mt-1 max-w-xs">
                        I remember our conversations. Ask me anything about health, symptoms, or medications.
                      </p>
                    </div>
                    <div className="grid grid-cols-2 gap-2 w-full max-w-xs">
                      {QUICK_PROMPTS.map((p) => (
                        <button
                          key={p}
                          onClick={() => sendMessage(p)}
                          className="text-xs px-3 py-2 rounded-xl border border-white/10 text-slate-400 hover:text-white hover:border-blue-500/40 hover:bg-blue-500/5 transition-all text-left"
                        >
                          {p}
                        </button>
                      ))}
                    </div>
                  </div>
                ) : (
                  <AnimatePresence initial={false}>
                    {messages.map((msg) => (
                      <motion.div
                        key={msg.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.25 }}
                        className={`mb-4 flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                      >
                        <div className={`max-w-[85%] flex flex-col gap-1 ${msg.role === "user" ? "items-end" : "items-start"}`}>
                          {msg.role === "assistant" && (
                            <div className="flex items-center gap-1.5 mb-1">
                              <div className="w-5 h-5 rounded-full bg-blue-500/20 flex items-center justify-center">
                                <Bot className="w-3 h-3 text-blue-400" />
                              </div>
                              <span className="text-xs text-slate-500">MedBot</span>
                            </div>
                          )}
                          <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap ${
                            msg.role === "user"
                              ? "bg-blue-600/80 text-white rounded-br-sm"
                              : "bg-slate-800/80 text-slate-100 border border-white/5 rounded-bl-sm"
                          }`}>
                            {msg.content}
                          </div>
                          <span className="text-[10px] text-slate-600">{formatTime(msg.timestamp)}</span>
                        </div>
                      </motion.div>
                    ))}
                    {isLoading && (
                      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start mb-4">
                        <div className="bg-slate-800/80 border border-white/5 px-4 py-3 rounded-2xl rounded-bl-sm flex items-center gap-2">
                          <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
                          <span className="text-xs text-slate-400">MedBot is thinking...</span>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                )}
              </ScrollArea>

              {/* Quick prompts row when chat has messages */}
              {messages.length > 0 && (
                <div className="px-4 pb-2 flex gap-2 overflow-x-auto scrollbar-hide">
                  {QUICK_PROMPTS.map((p) => (
                    <button
                      key={p}
                      onClick={() => sendMessage(p)}
                      className="shrink-0 text-xs px-3 py-1.5 rounded-xl border border-white/10 text-slate-400 hover:text-white hover:border-blue-500/40 hover:bg-blue-500/5 transition-all"
                    >
                      <Sparkles className="w-3 h-3 inline mr-1" />
                      {p}
                    </button>
                  ))}
                </div>
              )}

              {/* Input */}
              <div className="p-4 border-t border-white/5">
                <form
                  onSubmit={(e) => { e.preventDefault(); sendMessage(input); }}
                  className="flex gap-2"
                >
                  <Input
                    ref={inputRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask about symptoms, medications, health tips..."
                    className="flex-1 bg-slate-800/60 border-white/10 text-slate-100 placeholder:text-slate-500 focus-visible:ring-blue-500/40"
                    disabled={isLoading}
                  />
                  <Button
                    type="submit"
                    disabled={!input.trim() || isLoading}
                    className="bg-blue-600 hover:bg-blue-700 shrink-0"
                  >
                    {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                  </Button>
                </form>
                <p className="text-[10px] text-slate-600 mt-2 text-center">
                  MedBot is for informational purposes only. Always consult a real doctor for medical advice.
                </p>
              </div>
            </div>
          </div>
        </main>
      </SidebarInset>
    </SidebarProvider>
  );
}
'''.strip()

(chatbot_dir / "page.tsx").write_text(chatbot, encoding="utf-8")
print("Chatbot page written!")

# ---- 2. DOCTOR SUB-PAGES ----
doctor_dir = NeuroVision AI / "app" / "doctor"

# Patients page
patients_dir = doctor_dir / "patients"
patients_dir.mkdir(parents=True, exist_ok=True)
patients_page = r'''
"use client";
import React, { useState } from "react";
import { AppSidebar } from "@/components/app-sidebar";
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from "@/components/ui/breadcrumb";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Users, Search, Activity } from "lucide-react";

const MOCK_PATIENTS = [
  { id: "P001", name: "Sarah Jenkins", age: 34, condition: "Hypertension", status: "Active", lastVisit: "2026-04-01" },
  { id: "P002", name: "Michael Chen", age: 52, condition: "Type 2 Diabetes", status: "Critical", lastVisit: "2026-04-05" },
  { id: "P003", name: "Emma Watson", age: 28, condition: "Anxiety Disorder", status: "Stable", lastVisit: "2026-03-28" },
  { id: "P004", name: "David Miller", age: 45, condition: "Post-op Recovery", status: "Monitoring", lastVisit: "2026-04-03" },
  { id: "P005", name: "Alice Brown", age: 61, condition: "Cardiomegaly", status: "Active", lastVisit: "2026-03-20" },
];

export default function DoctorPatientsPage() {
  const [search, setSearch] = useState("");
  const filtered = MOCK_PATIENTS.filter(p =>
    p.name.toLowerCase().includes(search.toLowerCase()) ||
    p.condition.toLowerCase().includes(search.toLowerCase())
  );

  const statusColor: Record<string, string> = {
    Active: "bg-blue-500/20 text-blue-400 border-blue-500/30",
    Critical: "bg-red-500/20 text-red-400 border-red-500/30",
    Stable: "bg-green-500/20 text-green-400 border-green-500/30",
    Monitoring: "bg-orange-500/20 text-orange-400 border-orange-500/30",
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
              <BreadcrumbItem><BreadcrumbPage>My Patients</BreadcrumbPage></BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
        </header>
        <main className="p-6 space-y-6">
          <div className="flex flex-col md:flex-row justify-between md:items-center gap-4">
            <div>
              <h1 className="text-3xl font-bold flex items-center gap-2"><Users className="w-7 h-7 text-primary" /> My Patients</h1>
              <p className="text-muted-foreground mt-1">{filtered.length} patients found</p>
            </div>
            <div className="relative max-w-xs w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search patients..." className="pl-9" />
            </div>
          </div>
          <Card>
            <CardContent className="p-0">
              <table className="w-full text-sm">
                <thead className="border-b bg-muted/30">
                  <tr>
                    {["Patient ID", "Name", "Age", "Condition", "Last Visit", "Status", "Actions"].map(h => (
                      <th key={h} className="text-left p-4 font-medium text-muted-foreground">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {filtered.map(p => (
                    <tr key={p.id} className="hover:bg-muted/20 transition-colors">
                      <td className="p-4 font-mono text-xs text-muted-foreground">{p.id}</td>
                      <td className="p-4 font-semibold">{p.name}</td>
                      <td className="p-4">{p.age}</td>
                      <td className="p-4">{p.condition}</td>
                      <td className="p-4 text-muted-foreground">{p.lastVisit}</td>
                      <td className="p-4">
                        <span className={`px-2 py-1 rounded-full text-xs border ${statusColor[p.status] || ""}`}>{p.status}</span>
                      </td>
                      <td className="p-4">
                        <Button size="sm" variant="outline" className="gap-1">
                          <Activity className="w-3 h-3" /> View
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>
        </main>
      </SidebarInset>
    </SidebarProvider>
  );
}
'''.strip()
(patients_dir / "page.tsx").write_text(patients_page, encoding="utf-8")
print("Doctor patients page written!")

# Appointments page
appt_dir = doctor_dir / "appointments"
appt_dir.mkdir(parents=True, exist_ok=True)
appt_page = r'''
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

const BOOKING_KEY = "neurovision-all-bookings";

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
    const bc = typeof BroadcastChannel !== "undefined" ? new BroadcastChannel("neurovision-bookings") : null;
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
'''.strip()
(appt_dir / "page.tsx").write_text(appt_page, encoding="utf-8")
print("Doctor appointments page written!")

print("All files written successfully!")
