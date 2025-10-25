import type React from "react"
import { ThemeProvider } from "@/components/theme-provider"
import { AuthProvider } from "@/contexts/auth-context"
import { WebSocketProvider } from "@/contexts/websocket-context"
import { Toaster } from "@/components/ui/sonner"
import './globals.css'

export const metadata = {
  title: 'AgentFlow - AI Agent Platform',
  description: 'Build powerful AI agents that work for you',
  generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body suppressHydrationWarning>
        <AuthProvider>
          <WebSocketProvider>
            <ThemeProvider
              attribute="class"
              defaultTheme="system"
              enableSystem
              disableTransitionOnChange
            >
              {children}
              <Toaster />
            </ThemeProvider>
          </WebSocketProvider>
        </AuthProvider>
      </body>
    </html>
  )
}