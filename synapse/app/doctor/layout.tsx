"use client"

import { ProtectedRoute } from '@/lib/auth'

export default function DoctorLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ProtectedRoute allowedRoles={['DOCTOR']}>
      {children}
    </ProtectedRoute>
  )
}
