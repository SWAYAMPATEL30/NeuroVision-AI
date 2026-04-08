"use client"

import { ProtectedRoute } from '@/lib/auth'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ProtectedRoute allowedRoles={['PATIENT']}>
      {children}
    </ProtectedRoute>
  )
}

