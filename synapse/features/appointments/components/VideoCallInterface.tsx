"use client";

import React, { useState, useEffect, useRef } from 'react';
import { 
  Mic, MicOff, Video, VideoOff, PhoneOff, MessageSquare, 
  X, FileText, Clock, Send, Paperclip
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface ChatMessage {
  id: string;
  sender: 'patient' | 'doctor';
  text: string;
  time: string;
}

interface SharedFile {
  name: string;
  type: 'xray' | 'report';
}

interface Props {
  doctorName: string;
  doctorSpecialization: string;
  doctorPhoto: string;
  sharedFiles: SharedFile[];
  onEndCall: () => void;
}

export function VideoCallInterface({ doctorName, doctorSpecialization, doctorPhoto, sharedFiles, onEndCall }: Props) {
  const [micOn, setMicOn] = useState(true);
  const [camOn, setCamOn] = useState(true);
  const [showChat, setShowChat] = useState(false);
  const [showFiles, setShowFiles] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    { id: '1', sender: 'doctor', text: `Hello! I'm ${doctorName}. I can see your uploaded scans. Let me review them.`, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) },
  ]);
  const [inputText, setInputText] = useState('');
  const [callDuration, setCallDuration] = useState(0);
  const [callActive, setCallActive] = useState(true);
  const [showEndConfirm, setShowEndConfirm] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const localVideoRef = useRef<HTMLVideoElement>(null);

  // Call timer
  useEffect(() => {
    const interval = setInterval(() => {
      setCallDuration(d => d + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // Scroll chat to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Request camera access for local PiP
  useEffect(() => {
    if (camOn && localVideoRef.current && typeof window !== 'undefined') {
      navigator.mediaDevices?.getUserMedia({ video: true, audio: false })
        .then(stream => {
          if (localVideoRef.current) localVideoRef.current.srcObject = stream;
        })
        .catch(() => {/* user denied or no camera */});
    }
  }, [camOn]);

  const formatDuration = (secs: number) => {
    const m = Math.floor(secs / 60).toString().padStart(2, '0');
    const s = (secs % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  const sendMessage = () => {
    if (!inputText.trim()) return;
    const msg: ChatMessage = {
      id: Date.now().toString(),
      sender: 'patient',
      text: inputText.trim(),
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    setMessages(prev => [...prev, msg]);
    setInputText('');

    // Simulate doctor reply after 2s
    setTimeout(() => {
      const replies = [
        "I can see the scan clearly. Let me analyze it.",
        "The AI report looks comprehensive. Do you have any specific symptoms?",
        "Based on the report, I would recommend further tests.",
        "Please describe when these symptoms started.",
      ];
      const reply: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'doctor',
        text: replies[Math.floor(Math.random() * replies.length)],
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages(prev => [...prev, reply]);
    }, 2000);
  };

  const handleEndCall = () => {
    setCallActive(false);
    onEndCall();
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950 flex flex-col">
      {/* Top Bar */}
      <div className="flex items-center justify-between px-6 py-3 bg-black/40 border-b border-white/5 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <img src={doctorPhoto} alt={doctorName} className="w-9 h-9 rounded-full object-cover border-2 border-white/20"
            onError={(e) => { (e.target as HTMLImageElement).src = 'https://via.placeholder.com/36x36/1e293b/94a3b8?text=Dr'; }}
          />
          <div>
            <p className="text-sm font-bold text-white">{doctorName}</p>
            <p className="text-xs text-slate-400">{doctorSpecialization}</p>
          </div>
          <div className="ml-4 flex items-center gap-2 bg-emerald-500/20 border border-emerald-500/30 rounded-full px-3 py-1">
            <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
            <span className="text-xs font-bold text-emerald-400">Live</span>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-slate-800/60 rounded-full px-4 py-1.5">
            <Clock className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-sm font-mono text-white font-bold">{formatDuration(callDuration)}</span>
          </div>
        </div>
      </div>

      {/* Main Video Area */}
      <div className="flex-1 relative overflow-hidden">
        {/* Doctor Video (Simulated — full screen background) */}
        <div className="absolute inset-0 bg-gradient-to-br from-slate-800 to-slate-900 flex items-center justify-center">
          <div className="text-center space-y-3">
            <img
              src={doctorPhoto}
              alt={doctorName}
              className="w-28 h-28 rounded-full object-cover mx-auto border-4 border-white/10 shadow-2xl"
              onError={(e) => { (e.target as HTMLImageElement).src = 'https://via.placeholder.com/112x112/1e293b/94a3b8?text=Dr'; }}
            />
            <div className="space-y-1">
              <p className="text-white font-bold text-xl">{doctorName}</p>
              <p className="text-slate-400 text-sm">{doctorSpecialization}</p>
              <div className="flex items-center justify-center gap-2 mt-2">
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                <span className="text-xs text-emerald-400 font-medium">Video Connected</span>
              </div>
            </div>
          </div>
          {/* Simulated video feed pattern */}
          <div className="absolute inset-0 opacity-5"
            style={{
              backgroundImage: 'radial-gradient(circle at 50% 50%, rgba(59,130,246,0.4) 0%, transparent 70%)',
            }}
          />
        </div>

        {/* Local Video PiP (Bottom Right) */}
        <div className="absolute bottom-4 right-4 w-36 h-28 rounded-xl overflow-hidden border-2 border-white/10 shadow-2xl bg-slate-800 flex items-center justify-center">
          {camOn ? (
            <video ref={localVideoRef} autoPlay muted playsInline className="w-full h-full object-cover" />
          ) : (
            <div className="flex flex-col items-center gap-1">
              <VideoOff className="w-6 h-6 text-slate-500" />
              <span className="text-[10px] text-slate-500">Camera Off</span>
            </div>
          )}
          <div className="absolute bottom-1 left-1 text-[9px] text-white/60 bg-black/40 rounded px-1">You</div>
        </div>

        {/* Chat Sidebar */}
        <AnimatePresence>
          {showChat && (
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              className="absolute right-0 top-0 bottom-0 w-80 bg-slate-900/95 border-l border-white/5 flex flex-col backdrop-blur-xl"
            >
              <div className="flex items-center justify-between px-4 py-3 border-b border-white/5">
                <h3 className="font-bold text-white text-sm">Chat</h3>
                <button onClick={() => setShowChat(false)} className="text-slate-400 hover:text-slate-200">
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {messages.map(msg => (
                  <div key={msg.id} className={`flex ${msg.sender === 'patient' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[75%] rounded-2xl px-3 py-2 space-y-0.5 ${
                      msg.sender === 'patient' 
                        ? 'bg-blue-600 text-white rounded-br-sm' 
                        : 'bg-slate-800 text-slate-200 rounded-bl-sm'
                    }`}>
                      <p className="text-xs leading-relaxed">{msg.text}</p>
                      <p className={`text-[9px] ${msg.sender === 'patient' ? 'text-blue-200' : 'text-slate-500'}`}>{msg.time}</p>
                    </div>
                  </div>
                ))}
                <div ref={chatEndRef} />
              </div>
              <div className="p-3 border-t border-white/5">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={inputText}
                    onChange={e => setInputText(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && sendMessage()}
                    placeholder="Type a message..."
                    className="flex-1 bg-slate-800 border border-white/5 rounded-xl px-3 py-2 text-xs text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-blue-500/50"
                  />
                  <button
                    onClick={sendMessage}
                    className="w-9 h-9 bg-blue-600 rounded-xl flex items-center justify-center hover:bg-blue-500 transition-colors"
                  >
                    <Send className="w-4 h-4 text-white" />
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Shared Files Panel */}
        <AnimatePresence>
          {showFiles && (
            <motion.div
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              className="absolute left-0 top-0 bottom-0 w-72 bg-slate-900/95 border-r border-white/5 flex flex-col backdrop-blur-xl"
            >
              <div className="flex items-center justify-between px-4 py-3 border-b border-white/5">
                <h3 className="font-bold text-white text-sm flex items-center gap-2">
                  <Paperclip className="w-4 h-4 text-blue-400" />
                  Shared Files
                </h3>
                <button onClick={() => setShowFiles(false)} className="text-slate-400 hover:text-slate-200">
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div className="p-4 space-y-3">
                <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Sent to Doctor</p>
                {sharedFiles.map((file, i) => (
                  <div key={i} className="flex items-center gap-3 p-3 bg-slate-800/60 rounded-xl border border-white/5">
                    <span className="text-2xl">{file.type === 'xray' ? '🖼️' : '📊'}</span>
                    <div>
                      <p className="text-xs font-semibold text-slate-200">{file.name}</p>
                      <p className="text-[10px] text-slate-500 capitalize">{file.type === 'xray' ? 'Medical Scan' : 'AI Report'}</p>
                    </div>
                  </div>
                ))}
                <div className="mt-2 p-3 bg-emerald-500/10 rounded-xl border border-emerald-500/20">
                  <p className="text-xs text-emerald-400 font-medium">✓ Doctor has access to all files</p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Controls Bar */}
      <div className="px-6 py-4 bg-black/60 border-t border-white/5 backdrop-blur-md">
        <div className="flex items-center justify-center gap-4">
          {/* Mic */}
          <button
            onClick={() => setMicOn(m => !m)}
            className={`w-12 h-12 rounded-full flex items-center justify-center transition-all border ${
              micOn ? 'bg-slate-800 border-white/10 hover:bg-slate-700 text-white' : 'bg-red-500/20 border-red-500/40 text-red-400'
            }`}
          >
            {micOn ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />}
          </button>

          {/* Cam */}
          <button
            onClick={() => setCamOn(c => !c)}
            className={`w-12 h-12 rounded-full flex items-center justify-center transition-all border ${
              camOn ? 'bg-slate-800 border-white/10 hover:bg-slate-700 text-white' : 'bg-red-500/20 border-red-500/40 text-red-400'
            }`}
          >
            {camOn ? <Video className="w-5 h-5" /> : <VideoOff className="w-5 h-5" />}
          </button>

          {/* Files Panel */}
          <button
            onClick={() => { setShowFiles(f => !f); setShowChat(false); }}
            className={`w-12 h-12 rounded-full flex items-center justify-center transition-all border ${
              showFiles ? 'bg-blue-600 border-blue-500 text-white' : 'bg-slate-800 border-white/10 hover:bg-slate-700 text-white'
            }`}
          >
            <FileText className="w-5 h-5" />
          </button>

          {/* End Call */}
          <button
            onClick={() => setShowEndConfirm(true)}
            className="w-14 h-14 rounded-full bg-red-600 hover:bg-red-500 flex items-center justify-center transition-all shadow-xl shadow-red-900/40 border border-red-500"
          >
            <PhoneOff className="w-6 h-6 text-white" />
          </button>

          {/* Chat */}
          <button
            onClick={() => { setShowChat(c => !c); setShowFiles(false); }}
            className={`w-12 h-12 rounded-full flex items-center justify-center transition-all border ${
              showChat ? 'bg-blue-600 border-blue-500 text-white' : 'bg-slate-800 border-white/10 hover:bg-slate-700 text-white'
            }`}
          >
            <MessageSquare className="w-5 h-5" />
          </button>
        </div>

        {/* Labels */}
        <div className="flex items-center justify-center gap-4 mt-2">
          {[
            { label: micOn ? 'Mute' : 'Unmute', w: 'w-12' },
            { label: camOn ? 'Stop Video' : 'Start Video', w: 'w-12' },
            { label: 'Files', w: 'w-12' },
            { label: 'End Call', w: 'w-14' },
            { label: 'Chat', w: 'w-12' },
          ].map(item => (
            <span key={item.label} className={`${item.w} text-center text-[9px] text-slate-500`}>{item.label}</span>
          ))}
        </div>
      </div>

      {/* End Call Confirm Modal */}
      {showEndConfirm && (
        <div className="fixed inset-0 z-60 bg-black/70 flex items-center justify-center">
          <div className="bg-slate-900 rounded-2xl border border-white/10 p-6 w-80 space-y-4 text-center">
            <div className="w-12 h-12 rounded-full bg-red-500/20 flex items-center justify-center mx-auto border border-red-500/30">
              <PhoneOff className="w-6 h-6 text-red-400" />
            </div>
            <h3 className="text-lg font-bold text-white">End Call?</h3>
            <p className="text-sm text-slate-400">Are you sure you want to end this consultation?</p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowEndConfirm(false)}
                className="flex-1 py-2.5 bg-slate-800 text-slate-300 rounded-xl text-sm font-semibold hover:bg-slate-700 transition-colors"
              >
                Continue
              </button>
              <button
                onClick={handleEndCall}
                className="flex-1 py-2.5 bg-red-600 text-white rounded-xl text-sm font-bold hover:bg-red-500 transition-colors"
              >
                End Call
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
