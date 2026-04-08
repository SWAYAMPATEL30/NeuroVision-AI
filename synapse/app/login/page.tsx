"use client"

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { useAuth, Role } from '@/lib/auth'
import { Mail, Lock, Eye, EyeOff, Activity, ArrowRight, Loader2 } from 'lucide-react'
import { pageVariants, slideUp } from '@/lib/animations/variants'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()
  const { login } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    
    if (!email || !password) {
      setError('Please fill in all fields')
      return
    }

    setLoading(true)

    // Simulate API call
    setTimeout(() => {
      const emailLower = email.toLowerCase();
      let role: Role = 'PATIENT';
      let id = Date.now().toString();
      let name = email.split('@')[0];

      // Mapping dummy doctors to credentials
      const dummyDocs: Record<string, {id: string, name: string}> = {
        'ananya@doctor.com': { id: 'd1', name: 'Dr. Ananya Sharma' },
        'vikram@doctor.com': { id: 'd2', name: 'Dr. Vikram Mehta' },
        'rajesh@doctor.com': { id: 'd3', name: 'Dr. Rajesh Nair' },
        'priya@doctor.com': { id: 'd4', name: 'Dr. Priya Krishnamurthy' },
        'arun@doctor.com': { id: 'd5', name: 'Dr. Arun Gupta' },
        'sunita@doctor.com': { id: 'd6', name: 'Dr. Sunita Verma' },
      };

      if (dummyDocs[emailLower]) {
        role = 'DOCTOR';
        id = dummyDocs[emailLower].id;
        name = dummyDocs[emailLower].name;
      } else if (emailLower.includes('doctor')) {
        role = 'DOCTOR';
        name = "Guest Doctor";
      }
      
      login({
        id: id,
        name: name,
        email: email,
        role: role,
        photo: 'https://via.placeholder.com/150'
      }, 'dummy-jwt-token-xyz-123')
      
      setLoading(false);
    }, 1000)
  }

  return (
    <motion.div 
      initial="initial"
      animate="animate"
      exit="exit"
      variants={pageVariants}
      className="min-h-screen grid grid-cols-1 md:grid-cols-2 bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100"
    >
      {/* Visual Side */}
      <div className="hidden md:flex flex-col justify-center items-center bg-gradient-to-br from-blue-600 to-indigo-800 p-12 text-white relative overflow-hidden">
        <div className="absolute inset-0 opacity-20" style={{ backgroundImage: 'radial-gradient(circle at 50% 50%, #ffffff 2px, transparent 2px)', backgroundSize: '30px 30px' }} />
        <motion.div variants={slideUp} className="max-w-lg z-10 text-center space-y-6">
          <div className="w-20 h-20 bg-white/10 backdrop-blur-md rounded-2xl flex items-center justify-center mx-auto border border-white/20 shadow-2xl">
            <Activity className="w-10 h-10 text-blue-300" />
          </div>
          <h1 className="text-4xl font-black tracking-tight">Welcome back to Synapse</h1>
          <p className="text-blue-100 text-lg leading-relaxed">AI-Powered medical diagnostics and seamless doctor consultations in one unified platform.</p>
        </motion.div>
      </div>

      {/* Form Side */}
      <div className="flex flex-col justify-center px-8 md:px-16 lg:px-24">
        <div className="max-w-md w-full mx-auto space-y-8">
          <div className="text-center md:text-left space-y-2">
            <h2 className="text-3xl font-bold">Sign In</h2>
            <p className="text-slate-500 dark:text-slate-400 text-sm">Enter your credentials to access your account</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wide">Email Address</label>
              <div className="relative">
                <Mail className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input 
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className={`w-full pl-10 pr-4 py-3 bg-white dark:bg-slate-900 border rounded-xl focus:ring-2 focus:ring-blue-500/50 focus:outline-none transition-all ${error ? 'border-red-500 dark:border-red-500/50' : 'border-slate-200 dark:border-white/10'}`}
                  placeholder="you@example.com"
                />
              </div>
            </div>

            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-wide">Password</label>
                <a href="#forgot" className="text-xs text-blue-600 dark:text-blue-400 font-semibold hover:underline">Forgot password?</a>
              </div>
              <div className="relative">
                <Lock className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input 
                  type={showPassword ? "text" : "password"} 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={`w-full pl-10 pr-12 py-3 bg-white dark:bg-slate-900 border rounded-xl focus:ring-2 focus:ring-blue-500/50 focus:outline-none transition-all ${error ? 'border-red-500 dark:border-red-500/50' : 'border-slate-200 dark:border-white/10'}`}
                  placeholder="••••••••"
                />
                <button 
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {error && (
              <motion.p 
                initial={{ opacity: 0, x: -10 }} 
                animate={{ opacity: 1, x: 0 }} 
                className="text-xs font-semibold text-red-500 flex items-center gap-1.5"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-red-500" /> {error}
              </motion.p>
            )}

            <div className="flex items-center gap-2">
              <input type="checkbox" id="remember" className="rounded bg-slate-900 border-slate-700 text-blue-500 focus:ring-blue-500" />
              <label htmlFor="remember" className="text-sm font-medium text-slate-600 dark:text-slate-300">Remember me</label>
            </div>

            <button 
              type="submit" 
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3.5 rounded-xl transition-all shadow-lg shadow-blue-900/20 active:scale-[0.98] flex items-center justify-center gap-2"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>Sign In <ArrowRight className="w-4 h-4" /></>
              )}
            </button>
          </form>

          <p className="text-center text-sm text-slate-500 dark:text-slate-400">
            Don't have an account? <a href="/register" className="text-blue-600 dark:text-blue-400 font-bold hover:underline">Register</a>
          </p>
          
          <div className="pt-6 border-t border-slate-200 dark:border-white/5 text-center space-y-4">
            <p className="text-xs text-slate-500">Hint: Use any email with 'doctor' in it to test Doctor Dashboard.</p>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
