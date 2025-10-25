'use client'

import { createContext, useContext, useEffect, useRef, useState, ReactNode } from 'react'
import { useAuth } from '@/contexts/auth-context'
import { useToast } from '@/hooks/use-toast'
import { api } from '@/lib/api'
import { config } from '../lib/config'

interface CharacterEvent {
  id: string
  character_id: string
  event_type: string
  event_data: any
  message: {
    type: string
    data: any
  }
  timestamp: string
  created_at: string
}

interface Character {
  id: string
  name: string
  description: string
}

interface WebSocketContextType {
  events: CharacterEvent[]
  characters: Character[]
  connectionStatus: Map<string, 'connected' | 'disconnected' | 'connecting'>
  clearAllEvents: () => Promise<void>
  reconnectCharacter: (characterId: string) => void
  isConnected: boolean
  connectedCount: number
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined)

export function WebSocketProvider({ children }: { children: ReactNode }) {
  const [events, setEvents] = useState<CharacterEvent[]>([])
  const [characters, setCharacters] = useState<Character[]>([])
  const [connectionStatus, setConnectionStatus] = useState<Map<string, 'connected' | 'disconnected' | 'connecting'>>(new Map())
  const { token, isAuthenticated } = useAuth()
  const { toast } = useToast()

  // Auto-save events to localStorage whenever events change
  useEffect(() => {
    if (events.length > 0) {
      try {
        const eventsToSave = events.slice(0, 200) // Save last 200 events
        localStorage.setItem('character_events', JSON.stringify(eventsToSave))
      } catch (error) {
        console.error('Failed to save events to localStorage:', error)
      }
    }
  }, [events])

  // Load events from localStorage on mount
  useEffect(() => {
    try {
      const savedEvents = localStorage.getItem('character_events')
      if (savedEvents) {
        const parsedEvents = JSON.parse(savedEvents)
        setEvents(parsedEvents)
        console.log(`Loaded ${parsedEvents.length} events from localStorage`)
      }
    } catch (error) {
      console.error('Failed to load events from localStorage:', error)
    }
  }, [])

  // Use refs for WebSocket management to avoid React re-render issues
  const wsConnections = useRef<Map<string, WebSocket>>(new Map())
  const wsReconnectTimeouts = useRef<Map<string, NodeJS.Timeout>>(new Map())
  const wsPingIntervals = useRef<Map<string, NodeJS.Timeout>>(new Map())
  const isInitialized = useRef(false)

  // Cleanup function when user logs out
  useEffect(() => {
    if (!token || !isAuthenticated) {
      console.log('WebSocket Provider: User logged out, cleaning up connections')
      cleanupConnections()
      isInitialized.current = false
      setCharacters([])
      setEvents([])
      setConnectionStatus(new Map())
      sessionStorage.removeItem('websocket_state')
      localStorage.removeItem('character_events')
    }
  }, [token, isAuthenticated])

  const loadCharactersAndSetupConnections = async () => {
    try {
      console.log('WebSocket Provider: Loading characters and setting up connections')
      
      // Get all characters
      const charactersResponse = await api.getCharacters()
      if (charactersResponse.success && charactersResponse.data) {
        setCharacters(charactersResponse.data)
        
        // Load historical events for all characters
        const allEvents: CharacterEvent[] = []
        for (const character of charactersResponse.data) {
          try {
            const eventsResponse = await api.getCharacterEvents(character.id)
            if (eventsResponse.success && eventsResponse.data) {
              allEvents.push(...eventsResponse.data)
            }
          } catch (error) {
            console.error(`Failed to load events for character ${character.id}:`, error)
          }
        }
        
        // Sort events by timestamp (newest first)
        allEvents.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
        
        // Merge with existing events from localStorage (avoid duplicates)
        setEvents(currentEvents => {
          const existingIds = new Set(currentEvents.map(e => e.id))
          const newEvents = allEvents.filter(e => !existingIds.has(e.id))
          const mergedEvents = [...newEvents, ...currentEvents]
          
          // Sort and limit to 200 events
          mergedEvents.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
          return mergedEvents.slice(0, 200)
        })
        
        // Setup WebSocket connections with staggered timing
        charactersResponse.data.forEach((character, index) => {
          setTimeout(() => {
            connectWebSocket(character.id)
          }, index * 1000) // 1 second delay between connections
        })
        
        console.log(`WebSocket Provider: Initialized connections for ${charactersResponse.data.length} characters`)
      }
    } catch (error) {
      console.error('WebSocket Provider: Failed to load characters:', error)
      toast({
        title: "Connection Error",
        description: "Failed to initialize character monitoring. Please refresh the page.",
        variant: "destructive"
      })
    }
  }

  const connectWebSocket = (characterId: string) => {
    // Only connect on client side
    if (typeof window === 'undefined') {
      return
    }

    // Don't create duplicate connections
    if (wsConnections.current.has(characterId)) {
      const existingWs = wsConnections.current.get(characterId)
      if (existingWs && existingWs.readyState === WebSocket.OPEN) {
        console.log(`WebSocket already connected for character ${characterId}`)
        return
      }
    }

    const clientId = `monitor_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    const wsUrl = `${config.WS_BASE_URL}/${clientId}`
    const connectionStartTime = Date.now()
    
    try {
      setConnectionStatus(prev => new Map(prev.set(characterId, 'connecting')))
      
      if (!token) {
        console.error('No authentication token found')
        setConnectionStatus(prev => new Map(prev.set(characterId, 'disconnected')))
        return
      }
      
      const wsUrlWithAuth = `${wsUrl}?token=${encodeURIComponent(token)}`
      console.log(`WebSocket Provider: Connecting to character ${characterId}`)
      
      const ws = new WebSocket(wsUrlWithAuth)
      
      ws.onopen = () => {
        console.log(`WebSocket Provider: Connected to character ${characterId}`)
        setConnectionStatus(prev => new Map(prev.set(characterId, 'connected')))
        wsConnections.current.set(characterId, ws)
        
        // Send join room message immediately
        const joinMessage = {
          type: "join_room",
          room_id: `character_${characterId}`
        }
        
        try {
          ws.send(JSON.stringify(joinMessage))
          console.log(`WebSocket Provider: Joined room for character ${characterId}`)
        } catch (error) {
          console.error(`WebSocket Provider: Failed to join room for character ${characterId}:`, error)
        }
        
        // Setup ping interval
        setTimeout(() => {
          const pingInterval = setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
              try {
                ws.send(JSON.stringify({ 
                  type: 'ping',
                  timestamp: new Date().toISOString()
                }))
              } catch (error) {
                console.error(`WebSocket Provider: Failed to send ping for character ${characterId}:`, error)
              }
            }
          }, 30000)
          
          wsPingIntervals.current.set(characterId, pingInterval)
        }, 5000)
      }
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          if (data.type === 'room_joined') {
            console.log(`WebSocket Provider: Successfully joined room for character ${characterId}`)
          } else if (data.type === 'connection') {
            console.log(`WebSocket Provider: Connection established for character ${characterId}`)
          } else if (data.type === 'pong') {
            // Silent pong handling
          } else if (data.type === 'room_left' || data.type === 'echo') {
            // Handle system messages
          } else {
            // Real character event - add to events list
            const newEvent: CharacterEvent = {
              id: `ws_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
              character_id: characterId,
              event_type: data.type,
              event_data: data.data || data,
              message: data,
              timestamp: new Date().toISOString(),
              created_at: new Date().toISOString()
            }
            
            setEvents(prev => {
              // Check if event already exists
              const existingEvent = prev.find(e => 
                e.character_id === newEvent.character_id && 
                e.event_type === newEvent.event_type &&
                Math.abs(new Date(e.timestamp).getTime() - new Date(newEvent.timestamp).getTime()) < 1000 // Within 1 second
              )
              
              if (existingEvent) {
                return prev // Don't add duplicate
              }
              
              // Add new event and limit to 200 events
              const updatedEvents = [newEvent, ...prev]
              return updatedEvents.slice(0, 200)
            })
            
            // Show toast notification for new events
            const characterName = characters.find(c => c.id === characterId)?.name || 'Unknown Character'
            toast({
              title: "New Event",
              description: `${characterName}: ${data.type.replace(/_/g, ' ')}`,
            })
          }
        } catch (error) {
          console.error('WebSocket Provider: Error parsing message:', error)
        }
      }
      
      ws.onclose = (event) => {
        console.log(`WebSocket Provider: Disconnected from character ${characterId}. Code: ${event.code}, Time: ${Date.now() - connectionStartTime}ms`)
        setConnectionStatus(prev => new Map(prev.set(characterId, 'disconnected')))
        wsConnections.current.delete(characterId)
        
        // Clear ping interval
        const pingInterval = wsPingIntervals.current.get(characterId)
        if (pingInterval) {
          clearInterval(pingInterval)
          wsPingIntervals.current.delete(characterId)
        }
        
        // Don't reconnect for auth errors
        if (event.code === 1008) {
          console.error(`WebSocket Provider: Authentication failed for character ${characterId}`)
          return
        }
        
        // Auto-reconnect after 10 seconds
        const timeout = setTimeout(() => {
          console.log(`WebSocket Provider: Attempting to reconnect to character ${characterId}`)
          connectWebSocket(characterId)
        }, 10000)
        
        wsReconnectTimeouts.current.set(characterId, timeout)
      }
      
      ws.onerror = (error) => {
        const errorMsg = error instanceof Event ? 'Connection error' : error.message || 'Unknown error'
        console.error(`WebSocket Provider: Error for character ${characterId}:`, errorMsg)
        setConnectionStatus(prev => new Map(prev.set(characterId, 'disconnected')))
      }
      
    } catch (error) {
      console.error(`WebSocket Provider: Failed to create connection for character ${characterId}:`, error)
      setConnectionStatus(prev => new Map(prev.set(characterId, 'disconnected')))
    }
  }

  const cleanupConnections = () => {
    // Close all WebSocket connections
    wsConnections.current.forEach((ws, characterId) => {
      if (ws.readyState === WebSocket.OPEN) {
        console.log(`WebSocket Provider: Closing connection for character ${characterId}`)
        ws.close()
      }
    })
    
    // Clear all timeouts and intervals
    wsReconnectTimeouts.current.forEach(timeout => clearTimeout(timeout))
    wsPingIntervals.current.forEach(interval => clearInterval(interval))
    
    // Clear maps
    wsConnections.current.clear()
    wsReconnectTimeouts.current.clear()
    wsPingIntervals.current.clear()
    
    // Reset connection status
    setConnectionStatus(new Map())
  }

  const clearAllEvents = async () => {
    try {
      const clearPromises = characters.map(character => 
        api.clearCharacterEvents(character.id)
      )
      
      await Promise.all(clearPromises)
      setEvents([])
      
      toast({
        title: "Events Cleared",
        description: "All events have been cleared from the database.",
      })
    } catch (error) {
      console.error('Failed to clear events:', error)
      toast({
        title: "Error",
        description: "Failed to clear events from database. Please try again.",
        variant: "destructive"
      })
    }
  }

  const reconnectCharacter = (characterId: string) => {
    // Close existing connection if any
    const existingWs = wsConnections.current.get(characterId)
    if (existingWs) {
      existingWs.close()
      wsConnections.current.delete(characterId)
    }
    
    // Clear any existing timeouts
    const existingTimeout = wsReconnectTimeouts.current.get(characterId)
    if (existingTimeout) {
      clearTimeout(existingTimeout)
      wsReconnectTimeouts.current.delete(characterId)
    }
    
    // Create new connection
    connectWebSocket(characterId)
  }

  // Window beforeunload handler to maintain connections across page refreshes
  useEffect(() => {
    const handleBeforeUnload = () => {
      // Store connection state and events in sessionStorage to restore after refresh
      const connectionData = {
        characters: characters,
        events: events.slice(0, 100), // Store only last 100 events to avoid storage limit
        connectionStatus: Array.from(connectionStatus.entries()),
        timestamp: Date.now()
      }
      sessionStorage.setItem('websocket_state', JSON.stringify(connectionData))
    }

    window.addEventListener('beforeunload', handleBeforeUnload)
    
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload)
    }
  }, [characters, connectionStatus, events])

  // Restore connections on page load
  useEffect(() => {
    if (!token || !isAuthenticated || isInitialized.current) return

    const savedState = sessionStorage.getItem('websocket_state')
    if (savedState) {
      try {
        const parsedState = JSON.parse(savedState)
        // If saved state is less than 5 minutes old, restore it
        if (Date.now() - parsedState.timestamp < 5 * 60 * 1000) {
          console.log('WebSocket Provider: Restoring connection state and events from session')
          setCharacters(parsedState.characters)
          setEvents(parsedState.events || [])
          setConnectionStatus(new Map(parsedState.connectionStatus))
          
          // Re-establish connections
          parsedState.characters.forEach((character: Character, index: number) => {
            setTimeout(() => {
              connectWebSocket(character.id)
            }, index * 500)
          })
          
          isInitialized.current = true
          
          // Don't load from API since we restored from session
          return
        }
        // Clean up old state if too old
        sessionStorage.removeItem('websocket_state')
      } catch (error) {
        console.error('WebSocket Provider: Failed to restore state:', error)
      }
    }
    
    // If no valid session state, load from API
    if (!isInitialized.current) {
      loadCharactersAndSetupConnections()
      isInitialized.current = true
    }
  }, [token, isAuthenticated])

  const value = {
    events,
    characters,
    connectionStatus,
    clearAllEvents,
    reconnectCharacter,
    isConnected: Array.from(connectionStatus.values()).some(status => status === 'connected'),
    connectedCount: wsConnections.current.size
  }

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  )
}

export function useWebSocket() {
  const context = useContext(WebSocketContext)
  if (context === undefined) {
    throw new Error('useWebSocket must be used within a WebSocketProvider')
  }
  return context
}