"use client"

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuth } from '@/lib/auth'
import { 
  User, Mail, Phone, Calendar, Lock, Upload, MapPin, 
  Stethoscope, Building, Award, GraduationCap, ToggleLeft, Activity, ArrowRight, Loader2
} from 'lucide-react'
import { pageVariants, slideUp } from '@/lib/animations/variants'

type ActiveTab = 'patient' | 'doctor'

export default function RegisterPage() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('patient')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()
  const { register } = useAuth()

  // Common Fields
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  
  // Patient Fields
  const [dob, setDob] = useState('')
  const [gender, setGender] = useState('')

  // Doctor Fields
  const [specialty, setSpecialty] = useState('')
  const [license, setLicense] = useState('')
  const [degree, setDegree] = useState('')
  const [experience, setExperience] = useState('')
  const [clinic, setClinic] = useState('')
  const [clinicAddress, setClinicAddress] = useState('')
  const [consultLine, setConsultLine] = useState(false)
  const [consultClinic, setConsultClinic] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    
    if (!name || !email || !password || !confirmPassword) {
      setError('Please fill in all core fields')
      return
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    setLoading(true)

    // Simulating API Call
    setTimeout(async () => {
      if (activeTab === 'doctor') {
        const { supabase } = require('@/lib/supabaseClient')
        await supabase.from('doctors').insert({
          id: `doc_${Date.now()}`,
          name: name,
          email: email,
          specialization: specialty,
          degree: degree,
          experience: parseInt(experience) || 0,
          city: 'Unknown',
          clinicName: clinic,
          clinicAddress: clinicAddress,
          onlineAvailable: consultLine,
          offlineAvailable: consultClinic,
          avgRating: 5.0,
          reviewCount: 0
        })
      }

      register({
        id: Date.now().toString(),
        name,
        email,
        role: activeTab === 'doctor' ? 'DOCTOR' : 'PATIENT',
        specialization: specialty || undefined
      }, 'dummy-jwt-token-from-registration')
      
      setLoading(false)
    }, 1500)
  }

  return (
    <motion.div 
      initial="initial"
      animate="animate"
      exit="exit"
      variants={pageVariants}
      className="min-h-screen grid grid-cols-1 md:grid-cols-12 bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100"
    >
      {/* Decorative Side */}
      <div className="hidden md:flex md:col-span-4 lg:col-span-5 flex-col justify-center items-center bg-gradient-to-br from-indigo-700 to-blue-900 p-12 text-white relative overflow-hidden fixed h-screen top-0 left-0">
        <div className="absolute inset-0 opacity-20" style={{ backgroundImage: 'radial-gradient(circle at 50% 50%, #ffffff 2px, transparent 2px)', backgroundSize: '30px 30px' }} />
        <motion.div variants={slideUp} className="max-w-md z-10 space-y-6">
          <div className="w-16 h-16 bg-white/10 backdrop-blur-md rounded-2xl flex items-center justify-center border border-white/20 shadow-xl">
            <Activity className="w-8 h-8 text-blue-300" />
          </div>
          <h1 className="text-4xl font-black tracking-tight leading-tight">Join the Future of Healthcare</h1>
          <p className="text-blue-200 text-base leading-relaxed">
            {activeTab === 'patient' 
              ? 'Get precision AI diagnostics and book top specialists instantly. Your secure hub for personal medical records.'
              : 'Empower your practice with AI-assisted screening, seamless patient booking, and secure medical file management.'}
          </p>
        </motion.div>
      </div>

      {/* Main Registration Form */}
      <div className="md:col-span-8 lg:col-span-7 md:ml-[33.333333%] lg:ml-[41.666667%] px-6 py-12 md:px-16 lg:px-24 min-h-screen overflow-y-auto">
        <div className="max-w-2xl mx-auto space-y-8">
          <div>
            <h2 className="text-3xl font-bold">Create Account</h2>
            <p className="text-slate-500 dark:text-slate-400 mt-1">Join NeuroVision AI to access AI screening and healthcare tools</p>
          </div>

          <div className="flex p-1 bg-slate-200 dark:bg-slate-800/50 rounded-xl">
            <button 
              onClick={() => setActiveTab('patient')}
              className={`flex-1 py-3 text-sm font-bold rounded-lg transition-all flex items-center justify-center gap-2 ${activeTab === 'patient' ? 'bg-white dark:bg-slate-700 text-blue-600 dark:text-white shadow-sm' : 'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'}`}
            >
              <User className="w-4 h-4" /> Patient
            </button>
            <button 
              onClick={() => setActiveTab('doctor')}
              className={`flex-1 py-3 text-sm font-bold rounded-lg transition-all flex items-center justify-center gap-2 ${activeTab === 'doctor' ? 'bg-white dark:bg-slate-700 text-blue-600 dark:text-white shadow-sm' : 'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'}`}
            >
              <Stethoscope className="w-4 h-4" /> Doctor
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {/* Common Fields */}
              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-500 uppercase">Full Name</label>
                <div className="relative">
                  <User className="absolute left-3 top-3.5 w-4 h-4 text-slate-400" />
                  <input type="text" required value={name} onChange={e=>setName(e.target.value)} className="w-full pl-10 pr-4 py-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 rounded-xl text-sm outline-none focus:ring-2 focus:ring-blue-500" placeholder="John Doe" />
                </div>
              </div>
              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-500 uppercase">Email</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3.5 w-4 h-4 text-slate-400" />
                  <input type="email" required value={email} onChange={e=>setEmail(e.target.value)} className="w-full pl-10 pr-4 py-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 rounded-xl text-sm outline-none focus:ring-2 focus:ring-blue-500" placeholder="john@example.com" />
                </div>
              </div>
              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-500 uppercase">Phone Number</label>
                <div className="relative">
                  <Phone className="absolute left-3 top-3.5 w-4 h-4 text-slate-400" />
                  <input type="tel" value={phone} onChange={e=>setPhone(e.target.value)} className="w-full pl-10 pr-4 py-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 rounded-xl text-sm outline-none focus:ring-2 focus:ring-blue-500" placeholder="+1 (555) 000-0000" />
                </div>
              </div>
              
              {/* Conditional Fields: Patient */}
              {activeTab === 'patient' && (
                <>
                  <div className="space-y-1">
                    <label className="text-xs font-bold text-slate-500 uppercase">Date of Birth</label>
                    <div className="relative">
                      <Calendar className="absolute left-3 top-3.5 w-4 h-4 text-slate-400" />
                      <input type="date" value={dob} onChange={e=>setDob(e.target.value)} className="w-full pl-10 pr-4 py-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 rounded-xl text-sm outline-none focus:ring-2 focus:ring-blue-500" />
                    </div>
                  </div>
                  <div className="space-y-1 md:col-span-2">
                    <label className="text-xs font-bold text-slate-500 uppercase">Gender</label>
                    <select value={gender} onChange={e=>setGender(e.target.value)} className="w-full px-4 py-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 rounded-xl text-sm outline-none focus:ring-2 focus:ring-blue-500">
                      <option value="">Select Gender</option>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                </>
              )}

              {/* Conditional Fields: Doctor */}
              {activeTab === 'doctor' && (
                <>
                  <div className="space-y-1">
                    <label className="text-xs font-bold text-slate-500 uppercase">Specialization</label>
                    <div className="relative">
                      <Award className="absolute left-3 top-3.5 w-4 h-4 text-slate-400" />
                      <select required value={specialty} onChange={e=>setSpecialty(e.target.value)} className="w-full pl-10 pr-4 py-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 rounded-xl text-sm outline-none focus:ring-2 focus:ring-blue-500">
                        <option value="">Select Specialization</option>
                        <option value="Radiologist">Radiologist</option>
                        <option value="Orthopedic">Orthopedic</option>
                        <option value="Cardiologist">Cardiologist</option>
                        <option value="Neurologist">Neurologist</option>
                        <option value="General Physician">General Physician</option>
                      </select>
                    </div>
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs font-bold text-slate-500 uppercase">License Number</label>
                    <input type="text" required value={license} onChange={e=>setLicense(e.target.value)} className="w-full px-4 py-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 rounded-xl text-sm outline-none focus:ring-2 focus:ring-blue-500" placeholder="MCI-12345" />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs font-bold text-slate-500 uppercase">Graduation Degree</label>
                    <div className="relative">
                      <GraduationCap className="absolute left-3 top-3.5 w-4 h-4 text-slate-400" />
                      <input type="text" value={degree} onChange={e=>setDegree(e.target.value)} className="w-full pl-10 pr-4 py-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 rounded-xl text-sm outline-none focus:ring-2 focus:ring-blue-500" placeholder="MBBS, MD" />
                    </div>
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs font-bold text-slate-500 uppercase">Years of Exp.</label>
                    <input type="number" value={experience} onChange={e=>setExperience(e.target.value)} className="w-full px-4 py-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 rounded-xl text-sm outline-none focus:ring-2 focus:ring-blue-500" placeholder="e.g. 10" />
                  </div>
                  <div className="space-y-1 md:col-span-2">
                    <label className="text-xs font-bold text-slate-500 uppercase">Clinic/Hospital Name</label>
                    <div className="relative">
                      <Building className="absolute left-3 top-3.5 w-4 h-4 text-slate-400" />
                      <input type="text" value={clinic} onChange={e=>setClinic(e.target.value)} className="w-full pl-10 pr-4 py-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 rounded-xl text-sm outline-none focus:ring-2 focus:ring-blue-500" placeholder="Name of primary practice" />
                    </div>
                  </div>
                  <div className="space-y-1 md:col-span-2">
                    <label className="text-xs font-bold text-slate-500 uppercase">Clinic Address</label>
                    <div className="relative">
                      <MapPin className="absolute left-3 top-3.5 w-4 h-4 text-slate-400" />
                      <input type="text" value={clinicAddress} onChange={e=>setClinicAddress(e.target.value)} className="w-full pl-10 pr-4 py-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 rounded-xl text-sm outline-none focus:ring-2 focus:ring-blue-500" placeholder="Full address" />
                    </div>
                  </div>
                  <div className="space-y-2 md:col-span-2 p-4 border border-slate-200 dark:border-white/10 rounded-xl">
                    <label className="text-xs font-bold text-slate-500 uppercase">Consultation Modes</label>
                    <div className="flex gap-4">
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input type="checkbox" checked={consultLine} onChange={e=>setConsultLine(e.target.checked)} className="rounded bg-slate-900 border-slate-700 text-blue-500" />
                        <span className="text-sm font-medium">Online (Video)</span>
                      </label>
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input type="checkbox" checked={consultClinic} onChange={e=>setConsultClinic(e.target.checked)} className="rounded bg-slate-900 border-slate-700 text-blue-500" />
                        <span className="text-sm font-medium">Offline (In-Person)</span>
                      </label>
                    </div>
                  </div>
                </>
              )}

              {/* Passwords */}
              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-500 uppercase">Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3.5 w-4 h-4 text-slate-400" />
                  <input type="password" required value={password} onChange={e=>setPassword(e.target.value)} className="w-full pl-10 pr-4 py-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 rounded-xl text-sm outline-none focus:ring-2 focus:ring-blue-500" placeholder="••••••••" />
                </div>
              </div>
              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-500 uppercase">Confirm Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3.5 w-4 h-4 text-slate-400" />
                  <input type="password" required value={confirmPassword} onChange={e=>setConfirmPassword(e.target.value)} className="w-full pl-10 pr-4 py-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 rounded-xl text-sm outline-none focus:ring-2 focus:ring-blue-500" placeholder="••••••••" />
                </div>
              </div>

            </div>

            {error && (
              <p className="text-sm text-red-500 font-bold">{error}</p>
            )}

            <button 
              type="submit" 
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3.5 rounded-xl transition-all shadow-lg shadow-blue-900/20 active:scale-[0.98] flex items-center justify-center gap-2"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <>Create Account <ArrowRight className="w-4 h-4" /></>}
            </button>
            
            <p className="text-center text-sm text-slate-500 dark:text-slate-400">
              Already have an account? <a href="/login" className="text-blue-600 dark:text-blue-400 font-bold hover:underline">Sign In</a>
            </p>
          </form>
        </div>
      </div>
    </motion.div>
  )
}
