"use client"

import React from 'react'
import { motion } from 'framer-motion'
import { ShieldAlert, ArrowLeft } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth'

export default function UnauthorizedPage() {
  const router = useRouter()
  const { user } = useAuth()

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col items-center justify-center p-6 text-center">
      <motion.div 
        initial={{ opacity: 0, scale: 0.9 }} 
        animate={{ opacity: 1, scale: 1 }} 
        className="max-w-md w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 p-8 rounded-3xl shadow-2xl"
      >
        <div className="w-20 h-20 bg-red-100 dark:bg-red-500/20 text-red-600 dark:text-red-400 rounded-2xl flex items-center justify-center mx-auto mb-6 transform rotate-12">
          <ShieldAlert className="w-10 h-10" />
        </div>
        <h1 className="text-2xl font-black text-slate-900 dark:text-slate-100 mb-2">Access Denied</h1>
        <p className="text-slate-500 dark:text-slate-400 mb-8">
          You don't have permission to access the requested page. This area requires different privileges.
        </p>
        
        <div className="space-y-3">
          <button 
            onClick={() => router.push(user?.role === 'DOCTOR' ? '/doctor/dashboard' : '/dashboard')}
            className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-xl transition-all shadow-lg flex items-center justify-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" /> Return to Dashboard
          </button>
          
          <button 
            onClick={() => router.push('/login')}
            className="w-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-bold py-3 rounded-xl hover:bg-slate-200 dark:hover:bg-slate-700 transition-all border border-slate-200 dark:border-white/5"
          >
            Sign in with a different account
          </button>
        </div>
      </motion.div>
    </div>
  )
}
