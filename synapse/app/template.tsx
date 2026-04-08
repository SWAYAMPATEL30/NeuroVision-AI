"use client"

import { motion, AnimatePresence } from 'framer-motion'
import { usePathname } from 'next/navigation'
import { pageVariants } from '@/lib/animations/variants'
import { useEffect } from 'react'

export default function Template({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()

  // Reduced motion
  const isReducedMotion = typeof window !== 'undefined' 
    ? window.matchMedia('(prefers-reduced-motion: reduce)').matches 
    : false;

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={pathname}
        initial={isReducedMotion ? {} : "initial"}
        animate={isReducedMotion ? {} : "animate"}
        exit={isReducedMotion ? {} : "exit"}
        variants={pageVariants}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  )
}
