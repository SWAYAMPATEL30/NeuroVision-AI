"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
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
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Mic, MicOff, Volume2, VolumeX, Trash2, Brain, Heart, MessageSquare, AlertCircle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

// Type declarations for browser-native Web Speech API
declare global {
  interface Window {
    SpeechRecognition: new() => SpeechRecognition;
    webkitSpeechRecognition: new() => SpeechRecognition;
  }
  interface SpeechRecognition extends EventTarget {
    continuous: boolean;
    interimResults: boolean;
    lang: string;
    start(): void;
    stop(): void;
    onresult: ((this: SpeechRecognition, ev: any) => any) | null;
    onerror: ((this: SpeechRecognition, ev: any) => any) | null;
    onend: ((this: SpeechRecognition, ev: Event) => any) | null;
  }
}

interface Message {
  id: string;
  role: "user" | "therapist";
  text: string;
  timestamp: Date;
}

const STORAGE_KEY = "synapse-voice-therapist-history";

async function getTherapistResponse(userMessage: string, history: Message[]): Promise<string> {
  const systemPrompt = `You are a compassionate and professional mental health therapist named Aria. 
You listen carefully, ask thoughtful follow-up questions, and provide supportive responses.
Always respond with empathy, warmth, and professional insight. Keep responses concise (2-3 sentences).
Never diagnose. Encourage professional help for serious issues.`;

  try {
    const formData = new FormData();
    formData.append("message", userMessage);
    formData.append("history", JSON.stringify(history));
    formData.append("system_prompt", systemPrompt);

    const response = await fetch("http://localhost:8000/api/ai/chat", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      console.warn("AI Backend returned", response.status);
      return getFallbackResponse(userMessage);
    }

    const data = await response.json();
    return data.response || getFallbackResponse(userMessage);
  } catch (err) {
    console.error("AI Chat error:", err);
    return getFallbackResponse(userMessage);
  }
}

function getFallbackResponse(userMessage: string): string {
  const msg = userMessage.toLowerCase();
  if (msg.includes("sad") || msg.includes("depress") || msg.includes("unhappy"))
    return "I hear you, and I'm really glad you shared that with me. Feeling this way is hard, but you're not alone. Can you tell me more about when these feelings started?";
  if (msg.includes("anxious") || msg.includes("anxiety") || msg.includes("worry"))
    return "Anxiety can be really overwhelming. Let's take a moment to ground ourselves — focus on your breath. Would you like to try a quick grounding exercise together?";
  if (msg.includes("stress") || msg.includes("overwhelm"))
    return "It sounds like you're carrying a lot right now. That takes real courage to acknowledge. What's been weighing on you the most lately?";
  if (msg.includes("sleep") || msg.includes("insomnia") || msg.includes("tired"))
    return "Sleep difficulties can deeply affect how we feel everything else. How long has this been happening, and have you noticed any patterns before bedtime?";
  if (msg.includes("angry") || msg.includes("angry") || msg.includes("frustrat"))
    return "Anger is a valid emotion, and it's telling you something important. Let's explore what's underneath it — what situation recently made you feel this way?";
  if (msg.includes("lonely") || msg.includes("alone") || msg.includes("isolated"))
    return "Loneliness can be one of the most painful feelings. I'm here with you right now. How long have you been feeling this way?";
  return "Thank you for sharing that with me. I'm listening with full attention. Could you tell me more about how this is affecting your daily life?";
}

export default function VoiceTherapistPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [browserSupported, setBrowserSupported] = useState(true);

  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const synthRef = useRef<SpeechSynthesis | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Load history from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        setMessages(parsed.map((m: any) => ({ ...m, timestamp: new Date(m.timestamp) })));
      }
    } catch {}

    const SpeechRecAPI = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecAPI) {
      setBrowserSupported(false);
      setError("Voice recognition not supported. Please use Chrome or Edge.");
    } else {
      const recognition: any = new SpeechRecAPI();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = "en-US";

      recognition.onresult = (event: any) => {
        let interim = "";
        let final = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const txt = event.results[i][0].transcript;
          if (event.results[i].isFinal) final += txt;
          else interim += txt;
        }
        setTranscript(final || interim);
        if (final.trim()) handleUserSpeech(final.trim());
      };

      recognition.onerror = (event: any) => {
        if (event.error !== "no-speech") {
          setError(`Mic error: ${event.error}. Please check permissions.`);
        }
        setIsListening(false);
      };

      recognition.onend = () => setIsListening(false);
      recognitionRef.current = recognition;
    }

    synthRef.current = window.speechSynthesis;
  }, []);

  // Save history to localStorage whenever messages change
  useEffect(() => {
    if (messages.length > 0) {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
      } catch {}
    }
  }, [messages]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleUserSpeech = useCallback(async (text: string) => {
    setTranscript("");
    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      text,
      timestamp: new Date(),
    };
    setMessages(prev => {
      const updated = [...prev, userMsg];
      setIsProcessing(true);
      // Get AI response with full history
      getTherapistResponse(text, updated).then(response => {
        const therapistMsg: Message = {
          id: crypto.randomUUID(),
          role: "therapist",
          text: response,
          timestamp: new Date(),
        };
        setMessages(prev2 => [...prev2, therapistMsg]);
        setIsProcessing(false);
        // Speak the response using free Web Speech Synthesis API
        if (!isMuted && synthRef.current) {
          synthRef.current.cancel();
          const utterance = new SpeechSynthesisUtterance(response);
          utterance.rate = 0.9;
          utterance.pitch = 1.05;
          const voices = synthRef.current.getVoices();
          const femaleVoice = voices.find(v => v.name.includes("Female") || v.name.includes("Samantha") || v.name.includes("Karen") || v.name.includes("Google UK English Female"));
          if (femaleVoice) utterance.voice = femaleVoice;
          utterance.onstart = () => setIsSpeaking(true);
          utterance.onend = () => setIsSpeaking(false);
          synthRef.current.speak(utterance);
        }
      });
      return updated;
    });
  }, [isMuted]);

  const startListening = () => {
    if (!recognitionRef.current) return;
    setError(null);
    setTranscript("");
    recognitionRef.current.start();
    setIsListening(true);
  };

  const stopListening = () => {
    if (recognitionRef.current) recognitionRef.current.stop();
    setIsListening(false);
  };

  const toggleMute = () => {
    if (!isMuted && synthRef.current) synthRef.current.cancel();
    setIsMuted(!isMuted);
    setIsSpeaking(false);
  };

  const clearHistory = () => {
    setMessages([]);
    setTranscript("");
    localStorage.removeItem(STORAGE_KEY);
    if (synthRef.current) synthRef.current.cancel();
  };

  const formatTime = (d: Date) => d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset className="bg-gradient-to-br from-slate-950 via-purple-950/20 to-slate-950 text-slate-50">
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
                <BreadcrumbPage>Voice Therapist</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
          <div className="ml-auto flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={clearHistory} className="text-slate-400 hover:text-red-400 gap-2">
              <Trash2 className="w-4 h-4" /> Clear
            </Button>
            <Button variant="ghost" size="sm" onClick={toggleMute} className="text-slate-400 gap-2">
              {isMuted ? <VolumeX className="w-4 h-4 text-red-400" /> : <Volume2 className="w-4 h-4 text-purple-400" />}
              {isMuted ? "Muted" : "Sound On"}
            </Button>
          </div>
        </header>

        <main className="flex-1 overflow-hidden flex flex-col p-6">
          <div className="max-w-3xl mx-auto w-full flex flex-col h-full gap-6">
            {/* Header */}
            <div className="text-center space-y-2">
              <h1 className="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-purple-400 via-pink-300 to-violet-400 bg-clip-text text-transparent">
                Voice Therapist
              </h1>
              <p className="text-slate-400 text-sm">Speak freely. Your AI therapist is listening, remembering, and here for you.</p>
              <div className="flex justify-center gap-2 flex-wrap">
                <Badge variant="outline" className="border-purple-500/30 text-purple-400 text-xs gap-1">
                  <Brain className="w-3 h-3" /> AI-Powered
                </Badge>
                <Badge variant="outline" className="border-green-500/30 text-green-400 text-xs gap-1">
                  <Heart className="w-3 h-3" /> Empathetic
                </Badge>
                <Badge variant="outline" className="border-blue-500/30 text-blue-400 text-xs gap-1">
                  <MessageSquare className="w-3 h-3" /> Memory Enabled
                </Badge>
              </div>
            </div>

            {!browserSupported && (
              <div className="flex items-center gap-3 text-amber-300 text-sm bg-amber-500/10 p-4 rounded-xl border border-amber-500/20">
                <AlertCircle className="w-5 h-5 shrink-0" />
                Voice recognition requires Chrome or Edge browser. You can still read responses.
              </div>
            )}

            {error && (
              <div className="flex items-center gap-3 text-red-300 text-sm bg-red-500/10 p-4 rounded-xl border border-red-500/20">
                <AlertCircle className="w-5 h-5 shrink-0" />
                {error}
              </div>
            )}

            {/* Messages */}
            <Card className="flex-1 bg-slate-900/40 border-white/5 backdrop-blur overflow-hidden">
              <div ref={scrollRef} className="h-[380px] overflow-y-auto p-4">
                {messages.length === 0 && (
                  <div className="h-full flex flex-col items-center justify-center text-center gap-4 py-10">
                    <div className="w-20 h-20 rounded-full bg-purple-500/10 border border-purple-500/20 flex items-center justify-center">
                      <Brain className="w-10 h-10 text-purple-400" />
                    </div>
                    <div>
                      <p className="text-lg font-semibold text-slate-300">Hello, I&apos;m Aria</p>
                      <p className="text-sm text-slate-500 mt-1 max-w-xs">Your personal AI therapist. Press the mic and start talking — I&apos;ll remember your journey.</p>
                    </div>
                  </div>
                )}
                <AnimatePresence initial={false}>
                  {messages.map((msg) => (
                    <motion.div
                      key={msg.id}
                      initial={{ opacity: 0, y: 12 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3 }}
                      className={`mb-4 flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                    >
                      <div className={`max-w-[85%] ${msg.role === "user" ? "items-end" : "items-start"} flex flex-col gap-1`}>
                        <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                          msg.role === "user"
                            ? "bg-purple-600/80 text-white rounded-br-md"
                            : "bg-slate-800/80 text-slate-100 border border-white/5 rounded-bl-md"
                        }`}>
                          {msg.text}
                        </div>
                        <span className="text-[10px] text-slate-600">{msg.role === "therapist" ? "Aria • " : ""}{formatTime(msg.timestamp)}</span>
                      </div>
                    </motion.div>
                  ))}
                  {isProcessing && (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start mb-4">
                      <div className="bg-slate-800/80 border border-white/5 px-4 py-3 rounded-2xl rounded-bl-md">
                        <div className="flex gap-1 items-center h-4">
                          {[0, 1, 2].map(i => (
                            <motion.div key={i} className="w-2 h-2 rounded-full bg-purple-400"
                              animate={{ y: ["0%", "-50%", "0%"] }}
                              transition={{ duration: 0.6, delay: i * 0.2, repeat: Infinity }} />
                          ))}
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </Card>

            {/* Live Transcript */}
            {transcript && (
              <div className="bg-slate-900/60 border border-purple-500/20 rounded-xl px-4 py-3 text-sm text-slate-300 italic">
                &ldquo;{transcript}&rdquo;
              </div>
            )}

            {/* Mic Button */}
            <div className="flex flex-col items-center gap-4">
              <div className="relative">
                {isListening && (
                  <>
                    <motion.div
                      className="absolute inset-0 rounded-full bg-purple-500/20"
                      animate={{ scale: [1, 1.5, 2], opacity: [0.5, 0.2, 0] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    />
                    <motion.div
                      className="absolute inset-0 rounded-full bg-purple-500/15"
                      animate={{ scale: [1, 1.8, 2.5], opacity: [0.4, 0.15, 0] }}
                      transition={{ duration: 1.5, delay: 0.3, repeat: Infinity }}
                    />
                  </>
                )}
                {isSpeaking && (
                  <motion.div
                    className="absolute inset-0 rounded-full bg-green-500/20"
                    animate={{ scale: [1, 1.3, 1.6], opacity: [0.5, 0.25, 0] }}
                    transition={{ duration: 1.2, repeat: Infinity }}
                  />
                )}
                <button
                  onClick={isListening ? stopListening : startListening}
                  disabled={!browserSupported || isProcessing}
                  className={`relative w-24 h-24 rounded-full flex items-center justify-center shadow-2xl transition-all focus:outline-none focus:ring-4 focus:ring-purple-500/40 ${
                    isListening
                      ? "bg-gradient-to-br from-red-500 to-pink-600 scale-110"
                      : "bg-gradient-to-br from-purple-600 to-violet-700 hover:scale-105 active:scale-95"
                  } disabled:opacity-40 disabled:cursor-not-allowed`}
                >
                  {isListening ? <MicOff className="w-10 h-10 text-white" /> : <Mic className="w-10 h-10 text-white" />}
                </button>
              </div>
              <p className="text-xs text-slate-500 text-center">
                {isListening ? "🎙️ Listening... click to stop" 
                : isSpeaking ? "🔊 Aria is speaking..."
                : isProcessing ? "🤔 Processing your words..."
                : "Click the mic to start speaking"}
              </p>
            </div>
          </div>
        </main>
      </SidebarInset>
    </SidebarProvider>
  );
}
