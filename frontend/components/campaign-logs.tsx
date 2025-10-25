"use client"

import { useEffect, useState, useRef } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"

interface LogEntry {
  timestamp: string
  level: "info" | "warning" | "error" | "success"
  message: string
  data?: Record<string, any>
}

interface CampaignLogsProps {
  campaignId: string
}

export function CampaignLogs({ campaignId }: CampaignLogsProps) {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const eventSourceRef = useRef<EventSource | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Connect to SSE endpoint
    const eventSource = new EventSource(
      `http://localhost:8000/api/v1/campaigns/${campaignId}/logs`
    )

    eventSource.onopen = () => {
      console.log("SSE connection opened")
      setIsConnected(true)
    }

    eventSource.onmessage = (event) => {
      const logEntry: LogEntry = JSON.parse(event.data)
      setLogs((prev) => [...prev, logEntry])

      // Auto-scroll to bottom
      setTimeout(() => {
        if (scrollRef.current) {
          scrollRef.current.scrollTop = scrollRef.current.scrollHeight
        }
      }, 100)
    }

    eventSource.onerror = (error) => {
      console.error("SSE error:", error)
      setIsConnected(false)
      eventSource.close()
    }

    eventSourceRef.current = eventSource

    // Cleanup on unmount
    return () => {
      eventSource.close()
    }
  }, [campaignId])

  const getLevelColor = (level: string) => {
    switch (level) {
      case "info":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
      case "warning":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
      case "error":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
      case "success":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200"
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    })
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Campaign Logs</CardTitle>
            <CardDescription>Real-time progress updates</CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2">
              <div
                className={`h-2 w-2 rounded-full ${
                  isConnected ? "bg-green-500" : "bg-red-500"
                }`}
              />
              <span className="text-sm text-muted-foreground">
                {isConnected ? "Live" : "Disconnected"}
              </span>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px] w-full rounded-md border p-4" ref={scrollRef}>
          {logs.length === 0 ? (
            <div className="flex h-full items-center justify-center text-muted-foreground">
              Waiting for logs...
            </div>
          ) : (
            <div className="space-y-2">
              {logs.map((log, index) => (
                <div
                  key={index}
                  className="flex items-start gap-3 rounded-lg border p-3 text-sm"
                >
                  <span className="text-xs text-muted-foreground font-mono">
                    {formatTimestamp(log.timestamp)}
                  </span>
                  <Badge variant="outline" className={getLevelColor(log.level)}>
                    {log.level}
                  </Badge>
                  <div className="flex-1">
                    <p className="font-medium">{log.message}</p>
                    {log.data && Object.keys(log.data).length > 0 && (
                      <pre className="mt-1 text-xs text-muted-foreground overflow-auto">
                        {JSON.stringify(log.data, null, 2)}
                      </pre>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
