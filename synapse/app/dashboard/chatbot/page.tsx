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
import { Badge } from "@/components/ui/badge";

import { Send, Trash2, Bot, Sparkles, Loader2, HeartPulse } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const STORAGE_KEY = "synapse-chatbot-history";

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
  const systemPrompt = "You are MedBot, a medical assistant in Synapse. Help patients with health questions. Always recommend consulting a doctor. Be concise, empathetic, and clear.";

  try {
    const formData = new FormData();
    formData.append("message", userMessage);
    // Convert Role from "assistant" to "assistant" (backend expects text/role)
    const formattedHistory = history.map(m => ({
      role: m.role,
      text: m.content
    }));
    formData.append("history", JSON.stringify(formattedHistory));
    formData.append("system_prompt", systemPrompt);

    const res = await fetch("http://localhost:8000/api/ai/chat", {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      console.warn("AI Backend returned", res.status);
      return getFallbackReply(userMessage);
    }
    const data = await res.json();
    return data.response || getFallbackReply(userMessage);
  } catch (err) {
    console.error("AI Chat error:", err);
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
              <div
                id="chatbot-scroll-area"
                className="flex-1 p-4 overflow-y-auto"
                ref={scrollRef}
              >
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
              </div>

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