'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { api, LoginRequest, RegisterRequest } from '@/lib/api'

interface User {
  id: string
  email: string
  username: string
  is_active: boolean
  created_at: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  isLoading: boolean
  login: (credentials: LoginRequest) => Promise<{ success: boolean; error?: string }>
  register: (userData: RegisterRequest) => Promise<{ success: boolean; error?: string }>
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const savedToken = localStorage.getItem('access_token')
    const savedUser = localStorage.getItem('user')
    
    console.log('Loading saved auth data from localStorage:')
    console.log('Saved token:', savedToken ? 'exists' : 'not found')
    console.log('Saved user string:', savedUser)
    
    if (savedToken && savedUser) {
      try {
        const parsedUser = JSON.parse(savedUser)
        console.log('Parsed user object:', parsedUser)
        console.log('User email from localStorage:', parsedUser?.email)
        
        setToken(savedToken)
        setUser(parsedUser)
      } catch (error) {
        console.error('Error parsing saved user data:', error)
        // Clear corrupted data
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
      }
    }
    
    setIsLoading(false)
  }, [])

  const login = async (credentials: LoginRequest) => {
    try {
      console.log('Login attempt with credentials:', credentials)
      const response = await api.login(credentials)
      console.log('Login API response:', response)
      
      if (response.success && response.data) {
        const { access_token, user: userData } = response.data
        console.log('Extracted user data:', userData)
        console.log('User email from response:', userData?.email)
        
        localStorage.setItem('access_token', access_token)
        localStorage.setItem('user', JSON.stringify(userData))
        
        setToken(access_token)
        setUser(userData)
        
        return { success: true }
      } else {
        return { success: false, error: response.error || 'Login failed' }
      }
    } catch (error) {
      console.error('Login error:', error)
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Network error' 
      }
    }
  }

  const register = async (userData: RegisterRequest) => {
    try {
      const response = await api.register(userData)
      
      if (response.success && response.data) {
        const { access_token, user: newUser } = response.data
        
        localStorage.setItem('access_token', access_token)
        localStorage.setItem('user', JSON.stringify(newUser))
        
        setToken(access_token)
        setUser(newUser)
        
        return { success: true }
      } else {
        return { success: false, error: response.error || 'Registration failed' }
      }
    } catch (error) {
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Network error' 
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    setToken(null)
    setUser(null)
  }

  const value = {
    user,
    token,
    isLoading,
    login,
    register,
    logout,
    isAuthenticated: !!user && !!token
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}