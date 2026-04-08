"use client";

import React, { useEffect, useRef, useState } from 'react';
import {  lazy } from 'react'
import { useRouter } from 'next/navigation';
const Spline = lazy(() => import('@splinetool/react-spline'))


function HeroSplineBackground() {
  return (
    <div style={{
      position: 'relative',
      width: '100%',
      height: '100vh',
      pointerEvents: 'auto',
      overflow: 'hidden',
    }}>
      <Spline
        style={{
          width: '100%',
          height: '100vh',
          pointerEvents: 'auto',
        }}
        scene="https://prod.spline.design/us3ALejTXl6usHZ7/scene.splinecode"
      />
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100vh',
          background: `
            linear-gradient(to right, rgba(0, 0, 0, 0.8), transparent 30%, transparent 70%, rgba(0, 0, 0, 0.8)),
            linear-gradient(to bottom, transparent 50%, rgba(0, 0, 0, 0.9))
          `,
          pointerEvents: 'none',
        }}
      />
    </div>
  );
}

function HeroContent() {
  const router = useRouter();

  return (
    <div className="text-left text-white pt-20 sm:pt-28 md:pt-36 px-4 max-w-5xl">
      <h1 className="text-4xl sm:text-6xl md:text-7xl lg:text-8xl font-bold mb-6 leading-tight tracking-tight">
        The future of primary care is{' '}
        <span className="bg-gradient-to-r from-emerald-400 via-teal-500 to-cyan-500 bg-clip-text text-transparent">
          intelligent.
        </span>
      </h1>

      <p className="text-lg sm:text-xl md:text-2xl mb-8 opacity-90 max-w-3xl leading-relaxed font-medium">
        Synapse is a comprehensive, AI-powered health system. From clinical diagnostics like MRI and X-Ray analysis to 24/7 intelligent empathetic care, we bring world-class medicine to your fingertips.
      </p>

      <div className="mb-10 max-w-4xl">
        <p className="text-base sm:text-lg md:text-xl opacity-85 leading-relaxed">
          Skip the waiting room. Chat with our intelligent Medical Assistant, book instant clinical video consultations, or get instant AI-driven radiology reports. 
        </p>
      </div>

      <div className="flex flex-col sm:flex-row items-start space-y-4 sm:space-y-0 sm:space-x-6">
        <a
          href="/auth"
          className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-semibold py-3 px-8 rounded-full text-base transition-all duration-300 transform hover:scale-105 pointer-events-auto shadow-lg shadow-emerald-500/20"
        >
          Join Synapse Today
        </a>
        <a
          href="/dashboard"
          className="bg-white/10 hover:bg-white/20 text-white font-semibold py-3 px-8 rounded-full text-base transition-all duration-300 border border-white/20 backdrop-blur pointer-events-auto"
        >
          Go to Dashboard
        </a>
      </div>

      <div className="mt-10 grid grid-cols-2 sm:grid-cols-4 gap-4 opacity-90">
        <div className="bg-white/5 rounded-xl p-4 border border-white/10">
          <div className="text-xl font-bold">NeuroVision AI</div>
          <div className="text-xs text-white/70">Clinical image analysis</div>
        </div>
        <div className="bg-white/5 rounded-xl p-4 border border-white/10">
          <div className="text-xl font-bold">24/7 Access</div>
          <div className="text-xs text-white/70">Virtual primary care</div>
        </div>
        <div className="bg-white/5 rounded-xl p-4 border border-white/10">
          <div className="text-xl font-bold">Voice IA</div>
          <div className="text-xs text-white/70">Empathetic therapist</div>
        </div>
        <div className="bg-white/5 rounded-xl p-4 border border-white/10">
          <div className="text-xl font-bold">Same-Day</div>
          <div className="text-xs text-white/70">Video appointments</div>
        </div>
      </div>
    </div>
  );
}

function Navbar() {
  const [hoveredNavItem, setHoveredNavItem] = useState<string | null>(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-20" style={{ backgroundColor: 'rgba(13, 13, 24, 0.3)', backdropFilter: 'blur(8px)', WebkitBackdropFilter: 'blur(8px)', borderRadius: '0 0 15px 15px' }}>
      <div className="container mx-auto px-4 py-4 md:px-6 lg:px-8 flex items-center justify-between">
        <div className="flex items-center space-x-6 lg:space-x-8">
          <div className="text-white font-black text-2xl tracking-tighter bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
            synapse++
          </div>
          <div className="hidden lg:flex items-center space-x-6 text-sm text-gray-300 font-medium">
             <a href="#services" className="hover:text-white transition-colors">Services</a>
             <a href="#specialists" className="hover:text-white transition-colors">Specialists</a>
             <a href="#diagnostic" className="hover:text-white transition-colors">AI Diagnostics</a>
          </div>
        </div>

        <div className="flex items-center space-x-4 md:space-x-6">
          <a href="/auth" className="hidden lg:block text-white font-semibold text-sm hover:text-emerald-400 transition-colors">Log In</a>
          <a href="/dashboard" className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-2 px-5 rounded-full text-sm md:text-base transition-all duration-300">
            Secure Member Login
          </a>
          <button className="lg:hidden text-white p-2" onClick={toggleMobileMenu} aria-label="Toggle mobile menu">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d={isMobileMenuOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"} /></svg>
          </button>
        </div>
      </div>
    </nav>
  );
}

export const HeroSection = () => {
  const heroContentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleScroll = () => {
      if (heroContentRef.current) {
        requestAnimationFrame(() => {
          const scrollPosition = window.pageYOffset;
          const maxScroll = 400;
          const opacity = 1 - Math.min(scrollPosition / maxScroll, 1);
          heroContentRef.current!.style.opacity = opacity.toString();
        });
      }
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="relative">
      <Navbar />

      <div className="relative min-h-screen">
        <div className="absolute inset-0 z-0 pointer-events-auto">
          <HeroSplineBackground />
        </div>

        <div ref={heroContentRef} style={{
          position: 'absolute', top: 80, left: 0, width: '100%', height: 'calc(100vh - 80px)',
          display: 'flex', justifyContent: 'flex-start', alignItems: 'center', zIndex: 10, pointerEvents: 'none'
        }}>
          <div className="container mx-auto">
            <HeroContent />
          </div>
        </div>
      </div>

      <main className="relative z-10 bg-[#020617] text-slate-50 border-t border-white/5">
        <section id="services" className="container mx-auto px-4 py-20 md:py-32">
          <div className="max-w-3xl mb-16">
            <h2 className="text-3xl md:text-5xl font-black mb-6 tracking-tight text-white">Better healthcare, designed around you.</h2>
            <p className="text-slate-400 text-lg md:text-xl">
              We've created a seamless healthcare experience by combining top-tier medical professionals with proprietary AI diagnostic tools.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-slate-900/50 border border-white/5 p-8 rounded-3xl hover:bg-slate-900 transition-colors">
              <div className="w-12 h-12 bg-emerald-500/20 rounded-2xl flex items-center justify-center mb-6">
                <svg className="w-6 h-6 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
              </div>
              <h3 className="text-xl font-bold mb-3 text-white">Virtual Care 24/7</h3>
              <p className="text-slate-400 mb-6">Book video consultations with board-verified doctors instantly. Start treatment without stepping outside.</p>
              <a href="/dashboard/doctors" className="text-emerald-400 font-semibold hover:text-emerald-300">Book appt →</a>
            </div>
            
            <div className="bg-slate-900/50 border border-white/5 p-8 rounded-3xl hover:bg-slate-900 transition-colors">
               <div className="w-12 h-12 bg-purple-500/20 rounded-2xl flex items-center justify-center mb-6">
                <svg className="w-6 h-6 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
              </div>
              <h3 className="text-xl font-bold mb-3 text-white">NeuroVision AI</h3>
              <p className="text-slate-400 mb-6">Our proprietary models detect anomalies in Brain MRIs, Chest X-Rays, and Bone Scans with clinical precision.</p>
              <a href="/dashboard/neurovision" className="text-purple-400 font-semibold hover:text-purple-300">Run diagnostics →</a>
            </div>

            <div className="bg-slate-900/50 border border-white/5 p-8 rounded-3xl hover:bg-slate-900 transition-colors">
               <div className="w-12 h-12 bg-blue-500/20 rounded-2xl flex items-center justify-center mb-6">
                <svg className="w-6 h-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>
              </div>
              <h3 className="text-xl font-bold mb-3 text-white">Intelligent MedBot</h3>
              <p className="text-slate-400 mb-6">Got questions? Our medically-trained LLM provides instant, reliable, and empathetic health guidance anywhere.</p>
              <a href="/dashboard/chatbot" className="text-blue-400 font-semibold hover:text-blue-300">Chat now →</a>
            </div>
          </div>
        </section>

        <section className="border-t border-white/5 bg-slate-950 py-24">
          <div className="container mx-auto px-4 flex flex-col md:flex-row items-center gap-16">
            <div className="md:w-1/2">
              <img src="https://images.unsplash.com/photo-1576091160550-2173dcae57de?auto=format&fit=crop&w=800&q=80" alt="Doctor consulting" className="rounded-2xl shadow-2xl border border-white/10" />
            </div>
            <div className="md:w-1/2 max-w-2xl">
              <h2 className="text-3xl md:text-4xl font-bold mb-6 text-white">Your personal health hub.</h2>
              <ul className="space-y-6">
                <li className="flex gap-4">
                  <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400 font-bold shrink-0">1</div>
                  <div>
                    <h4 className="text-lg font-bold text-white">Download Clinical Reports</h4>
                    <p className="text-slate-400">Instantly generate and download PDF summaries of all your AI scans and remote consultations.</p>
                  </div>
                </li>
                 <li className="flex gap-4">
                  <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400 font-bold shrink-0">2</div>
                  <div>
                    <h4 className="text-lg font-bold text-white">Secure Records</h4>
                    <p className="text-slate-400">All data is kept secure on our decentralized vault. You control who has access to your medical history.</p>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </section>

        <footer className="border-t border-white/5 py-12 text-center text-slate-500">
          <p>© {new Date().getFullYear()} Synapse Medical AI. All rights reserved.</p>
        </footer>
      </main>
    </div>
  );
};

  
