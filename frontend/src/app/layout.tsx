import type { Metadata } from 'next'
import { AuthProvider } from '@/src/lib/auth/auth-context'
import '@/src/styles/globals.css'

export const metadata: Metadata = {
  title: 'Taskie - Todo App',
  description: 'A modern todo application for task management',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  )
}
