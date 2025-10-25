"use client"

import { useState, useEffect } from "react"
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Clock,
  RefreshCw,
  Server,
  Settings,
  XCircle,
} from "lucide-react"
import Link from "next/link"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { DashboardHeader } from "@/components/dashboard-header"

interface ApiInfo {
  name: string
  version: string
  description: string
  endpoints: {
    [key: string]: {
      path: string
      methods: string[]
      description: string
    }
  }
}

interface HealthStatus {
  system_overview: {
    status: string
    last_updated: string
    last_incident: string
    environment: string
    version: string
  }
  services: {
    [key: string]: {
      name: string
      status: string
      uptime: string
      response_time: string
      requests_min: number
      issues: string[]
    }
  }
}

interface DetailedMetrics {
  timestamp: string
  resources: {
    cpu: {
      current: number
      average: number
      peak: number
      cores: number
      frequency: number
    }
    memory: {
      current: number
      average: number
      peak: number
      total_gb: number
      used_gb: number
      available_gb: number
    }
    storage: {
      current: number
      average: number
      peak: number
      total_gb: number
      used_gb: number
      free_gb: number
    }
  }
  network: {
    traffic: {
      inbound_mbps: number
      outbound_mbps: number
      peak_mbps: number
    }
    total_requests_24h: number
    bytes_sent_total: number
    bytes_recv_total: number
  }
  application: {
    process_count: number
    characters_count: number
    active_conversations: number
    social_posts_today: number
    websocket_connections: number
    uptime_seconds: number
  }
  system_info: {
    platform: string
    python_version: string
    boot_time: string
    environment: string
  }
  trends: {
    cpu_trend: string
    memory_trend: string
    disk_trend: string
    network_trend: string
  }
  alerts: string[]
  recommendations: string[]
}

export default function SystemStatusPage() {
  const [apiInfo, setApiInfo] = useState<ApiInfo | null>(null)
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null)
  const [detailedMetrics, setDetailedMetrics] = useState<DetailedMetrics | null>(null)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())
  const [error, setError] = useState<string | null>(null)
  const [loadingStates, setLoadingStates] = useState({
    api: true,
    health: true,
    metrics: true
  })

  const fetchSystemStatus = async () => {
    try {
      setError(null)
      console.log('Starting API calls...')
      
      // Fetch API info
      try {
        setLoadingStates(prev => ({ ...prev, api: true }))
        console.log('Fetching API info from http://localhost:8000/api')
        const apiResponse = await fetch('http://localhost:8000/api')
        if (!apiResponse.ok) {
          throw new Error(`API endpoint failed: ${apiResponse.status}`)
        }
        const apiData = await apiResponse.json()
        console.log('API data received:', apiData)
        console.log('API endpoints structure:', apiData.endpoints)
        console.log('Endpoints keys:', apiData.endpoints ? Object.keys(apiData.endpoints) : 'no endpoints')
        setApiInfo(apiData)
        setLoadingStates(prev => ({ ...prev, api: false }))
      } catch (err) {
        console.error('API fetch error:', err)
        setLoadingStates(prev => ({ ...prev, api: false }))
      }

      // Fetch health status
      try {
        setLoadingStates(prev => ({ ...prev, health: true }))
        console.log('Fetching health status from http://localhost:8000/health')
        const healthResponse = await fetch('http://localhost:8000/health')
        if (!healthResponse.ok) {
          throw new Error(`Health endpoint failed: ${healthResponse.status}`)
        }
        const healthData = await healthResponse.json()
        console.log('Health data received:', healthData)
        setHealthStatus(healthData)
        setLoadingStates(prev => ({ ...prev, health: false }))
      } catch (err) {
        console.error('Health fetch error:', err)
        setLoadingStates(prev => ({ ...prev, health: false }))
      }

      // Fetch detailed metrics
      try {
        setLoadingStates(prev => ({ ...prev, metrics: true }))
        console.log('Fetching detailed metrics from http://localhost:8000/metrics/detailed')
        const metricsResponse = await fetch('http://localhost:8000/metrics/detailed')
        if (!metricsResponse.ok) {
          throw new Error(`Metrics endpoint failed: ${metricsResponse.status}`)
        }
        const metricsData = await metricsResponse.json()
        console.log('Metrics data received:', metricsData)
        setDetailedMetrics(metricsData)
        setLoadingStates(prev => ({ ...prev, metrics: false }))
      } catch (err) {
        console.error('Metrics fetch error:', err)
        setLoadingStates(prev => ({ ...prev, metrics: false }))
      }

      setLastUpdated(new Date())
    } catch (err) {
      console.error('General fetch error:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch system status')
    }
  }

  const handleRefresh = async () => {
    setIsRefreshing(true)
    await fetchSystemStatus()
    setIsRefreshing(false)
  }

  useEffect(() => {
    fetchSystemStatus()
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchSystemStatus, 30000)
    return () => clearInterval(interval)
  }, [])

  // Calculate overall system status
  const getOverallStatus = () => {
    if (error) return "outage"
    if (!healthStatus) return "unknown"
    
    return healthStatus.system_overview?.status || "unknown"
  }

  const overallStatus = getOverallStatus()

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400)
    const hours = Math.floor((seconds % 86400) / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    
    if (days > 0) return `${days}d ${hours}h ${minutes}m`
    if (hours > 0) return `${hours}h ${minutes}m`
    return `${minutes}m`
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "operational":
      case "healthy":
        return "default"
      case "degraded":
      case "warning":
        return "outline"
      case "outage":
      case "unhealthy":
        return "destructive"
      default:
        return "secondary"
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "operational":
      case "healthy":
        return <CheckCircle2 className="h-4 w-4" />
      case "degraded":
      case "warning":
        return <AlertTriangle className="h-4 w-4" />
      case "outage":
      case "unhealthy":
        return <XCircle className="h-4 w-4" />
      default:
        return <Server className="h-4 w-4" />
    }
  }

  return (
    <div className="flex flex-col w-full">
      <DashboardHeader 
        breadcrumbs={[
          { title: "System", href: "/system" },
          { title: "Status" }
        ]}
      >
        <Button variant="outline" size="sm" className="h-8 gap-1" onClick={handleRefresh} disabled={isRefreshing}>
          <RefreshCw className={`h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
          <span>Refresh</span>
        </Button>
        <Button asChild variant="outline" size="sm" className="h-8 gap-1">
          <Link href="/settings">
            <Settings className="h-4 w-4" />
            <span>Settings</span>
          </Link>
        </Button>
      </DashboardHeader>

      <div className="flex-1 p-4 md:p-6">
        <div className="mx-auto max-w-6xl space-y-6">

          {/* System Overview */}
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>System Overview</CardTitle>
                  <CardDescription>Current status of backend services</CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={getStatusColor(overallStatus)} className="px-3 py-1">
                    {getStatusIcon(overallStatus)}
                    <span className="ml-1 capitalize">{overallStatus}</span>
                  </Badge>
                  <span className="text-sm text-muted-foreground">
                    Last updated: {lastUpdated.toLocaleTimeString()}
                  </span>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {error ? (
                <div className="flex h-40 flex-col items-center justify-center rounded-lg border border-dashed border-red-200">
                  <XCircle className="h-10 w-10 text-red-500" />
                  <h3 className="mt-4 text-lg font-medium text-red-700">Connection Error</h3>
                  <p className="mt-2 text-sm text-red-600">{error}</p>
                  <Button onClick={handleRefresh} className="mt-4" variant="outline" size="sm">
                    Try Again
                  </Button>
                </div>
              ) : (
                <div className="grid gap-4 md:grid-cols-2">
                  {/* API Information */}
                  <div className="rounded-lg border p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <Server className="h-5 w-5 text-muted-foreground" />
                        <h3 className="font-medium">API Service</h3>
                      </div>
                      <Badge variant={apiInfo ? "default" : "secondary"}>
                        {apiInfo ? (
                          <>
                            <CheckCircle2 className="mr-1 h-3 w-3" />
                            Online
                          </>
                        ) : (
                          "Loading..."
                        )}
                      </Badge>
                    </div>
                    {apiInfo && (
                      <div className="space-y-2 text-sm">
                        <div className="flex items-center justify-between">
                          <span className="text-muted-foreground">Name</span>
                          <span>{apiInfo.name}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-muted-foreground">Version</span>
                          <span>{apiInfo.version}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-muted-foreground">Endpoints</span>
                          <span>{apiInfo.endpoints ? Object.keys(apiInfo.endpoints).length : 0}</span>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Health Status */}
                  <div className="rounded-lg border p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <Activity className="h-5 w-5 text-muted-foreground" />
                        <h3 className="font-medium">Health Status</h3>
                      </div>
                      <Badge variant={healthStatus ? getStatusColor(healthStatus.status) : "secondary"}>
                        {healthStatus ? (
                          <>
                            {getStatusIcon(healthStatus.status)}
                            <span className="ml-1 capitalize">{healthStatus.status}</span>
                          </>
                        ) : (
                          "Loading..."
                        )}
                      </Badge>
                    </div>
                    {healthStatus && (
                      <div className="space-y-2 text-sm">
                        <div className="flex items-center justify-between">
                          <span className="text-muted-foreground">Version</span>
                          <span>{healthStatus.system_overview?.version || "N/A"}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-muted-foreground">Environment</span>
                          <span>{healthStatus.system_overview?.environment || "N/A"}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-muted-foreground">Services</span>
                          <span>{healthStatus.services ? Object.keys(healthStatus.services).length : 0}</span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <div className="grid gap-6 md:grid-cols-2">
            {/* Health Checks */}
            <Card>
              <CardHeader>
                <CardTitle>Health Checks</CardTitle>
                <CardDescription>Detailed status of system components</CardDescription>
              </CardHeader>
              <CardContent>
                {loadingStates.health ? (
                  <div className="flex h-40 flex-col items-center justify-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                    <p className="mt-2 text-sm text-muted-foreground">Loading health checks...</p>
                  </div>
                ) : healthStatus && healthStatus.services ? (
                  <div className="space-y-4">
                    {Object.entries(healthStatus.services).map(([key, service]) => (
                      <div key={key} className="rounded-lg border p-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium">
                              {service.name}
                            </span>
                          </div>
                          <Badge variant={getStatusColor(service.status)} size="sm">
                            {getStatusIcon(service.status)}
                            <span className="ml-1 capitalize">{service.status}</span>
                          </Badge>
                        </div>
                        <div className="mt-2 space-y-1 text-xs text-muted-foreground">
                          <div>Uptime: {service.uptime}</div>
                          <div>Response time: {service.response_time}</div>
                          <div>Requests/min: {service.requests_min}</div>
                          {service.issues.length > 0 && (
                            <div className="text-red-600">Issues: {service.issues.join(', ')}</div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="flex h-40 flex-col items-center justify-center rounded-lg border border-dashed">
                    <XCircle className="h-10 w-10 text-muted-foreground" />
                    <h3 className="mt-4 text-lg font-medium">No Health Data</h3>
                    <p className="mt-2 text-sm text-muted-foreground">Unable to load health check information</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* API Endpoints */}
            <Card>
              <CardHeader>
                <CardTitle>API Endpoints</CardTitle>
                <CardDescription>Available service endpoints and documentation</CardDescription>
              </CardHeader>
              <CardContent>
                {loadingStates.api ? (
                  <div className="flex h-40 flex-col items-center justify-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                    <p className="mt-2 text-sm text-muted-foreground">Loading endpoints...</p>
                  </div>
                ) : apiInfo ? (
                  // Debug: show raw API data if endpoints structure is different
                  !apiInfo.endpoints ? (
                    <div className="space-y-4">
                      <div className="rounded-lg bg-yellow-50 border border-yellow-200 p-4">
                        <h4 className="text-sm font-medium text-yellow-800 mb-2">Raw API Response</h4>
                        <pre className="text-xs text-yellow-700 overflow-auto bg-yellow-100 p-2 rounded">
                          {JSON.stringify(apiInfo, null, 2)}
                        </pre>
                      </div>
                    </div>
                  ) : (
                  <div className="space-y-4 max-h-96 overflow-y-auto">
                    {/* API Info Header */}
                    <div className="rounded-lg bg-muted/50 p-4 border">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="text-sm font-semibold">Service Information</h4>
                        <Badge variant="secondary">{apiInfo.version}</Badge>
                      </div>
                      <p className="text-xs text-muted-foreground mb-2">{apiInfo.description}</p>
                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <span>Base URL: <code className="bg-muted px-1 rounded">http://localhost:8000</code></span>
                        <span>Endpoints: {Object.keys(apiInfo.endpoints).length}</span>
                      </div>
                    </div>

                    {/* Endpoints List */}
                    <div className="space-y-3">
                      {Object.entries(apiInfo.endpoints).map(([name, endpoint]) => {
                        const getMethodColor = (method: string) => {
                          switch (method.toUpperCase()) {
                            case 'GET': return 'bg-green-100 text-green-800 border-green-200'
                            case 'POST': return 'bg-blue-100 text-blue-800 border-blue-200'
                            case 'PUT': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
                            case 'DELETE': return 'bg-red-100 text-red-800 border-red-200'
                            case 'PATCH': return 'bg-purple-100 text-purple-800 border-purple-200'
                            default: return 'bg-gray-100 text-gray-800 border-gray-200'
                          }
                        }

                        return (
                          <div key={name} className="rounded-lg border p-4 hover:bg-muted/30 transition-colors">
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex-1 min-w-0">
                                <h5 className="text-sm font-medium truncate">{name}</h5>
                                <div className="mt-1 flex items-center gap-2 flex-wrap">
                                  <code className="text-xs bg-muted px-2 py-1 rounded font-mono text-muted-foreground">
                                    {endpoint.path}
                                  </code>
                                </div>
                              </div>
                              <div className="flex gap-1 ml-2 flex-shrink-0">
                                {endpoint.methods?.map((method) => (
                                  <span 
                                    key={method} 
                                    className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium border ${getMethodColor(method)}`}
                                  >
                                    {method.toUpperCase()}
                                  </span>
                                ))}
                              </div>
                            </div>
                            
                            {endpoint.description && (
                              <p className="text-xs text-muted-foreground leading-relaxed">
                                {endpoint.description}
                              </p>
                            )}
                            
                            {/* Additional endpoint details if available */}
                            <div className="mt-2 flex items-center gap-3 text-xs text-muted-foreground">
                              <span className="flex items-center gap-1">
                                <Server className="h-3 w-3" />
                                REST API
                              </span>
                              {endpoint.methods?.includes('GET') && (
                                <span className="flex items-center gap-1">
                                  <CheckCircle2 className="h-3 w-3 text-green-500" />
                                  Public
                                </span>
                              )}
                            </div>
                          </div>
                        )
                      })}
                    </div>

                    {/* API Documentation Footer */}
                    <div className="mt-4 p-3 rounded-lg bg-blue-50 border border-blue-200">
                      <div className="flex items-center gap-2">
                        <Activity className="h-4 w-4 text-blue-600" />
                        <span className="text-sm font-medium text-blue-900">API Documentation</span>
                      </div>
                      <p className="text-xs text-blue-700 mt-1">
                        Full API documentation is available at <code className="bg-blue-100 px-1 rounded">http://localhost:8000/docs</code>
                      </p>
                    </div>
                  </div>
                  )
                ) : (
                  <div className="flex h-40 flex-col items-center justify-center rounded-lg border border-dashed">
                    <XCircle className="h-10 w-10 text-muted-foreground" />
                    <h3 className="mt-4 text-lg font-medium">No API Data</h3>
                    <p className="mt-2 text-sm text-muted-foreground">Unable to load API endpoint information</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Detailed Metrics */}
          <Card>
            <CardHeader>
              <CardTitle>Detailed Metrics</CardTitle>
              <CardDescription>Comprehensive system performance metrics</CardDescription>
            </CardHeader>
            <CardContent>
              {loadingStates.metrics ? (
                <div className="flex h-40 flex-col items-center justify-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                  <p className="mt-2 text-sm text-muted-foreground">Loading detailed metrics...</p>
                </div>
              ) : detailedMetrics ? (
                <div className="grid gap-6 md:grid-cols-3">
                  {/* System Resources */}
                  <div className="space-y-4">
                    <h4 className="text-sm font-medium">System Resources</h4>
                    <div className="space-y-3">
                      <div className="rounded-lg border p-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-muted-foreground">CPU Usage</span>
                          <span className="text-sm font-medium">{detailedMetrics.resources?.cpu?.current || 0}%</span>
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">
                          Cores: {detailedMetrics.resources?.cpu?.cores || 0} | Freq: {detailedMetrics.resources?.cpu?.frequency || 0}MHz
                        </div>
                      </div>
                      <div className="rounded-lg border p-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-muted-foreground">Memory Usage</span>
                          <span className="text-sm font-medium">{detailedMetrics.resources?.memory?.current || 0}%</span>
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">
                          {detailedMetrics.resources?.memory?.used_gb || 0}GB / {detailedMetrics.resources?.memory?.total_gb || 0}GB
                        </div>
                      </div>
                      <div className="rounded-lg border p-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-muted-foreground">Storage Usage</span>
                          <span className="text-sm font-medium">{detailedMetrics.resources?.storage?.current || 0}%</span>
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">
                          {detailedMetrics.resources?.storage?.used_gb || 0}GB / {detailedMetrics.resources?.storage?.total_gb || 0}GB
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Network & Application */}
                  <div className="space-y-4">
                    <h4 className="text-sm font-medium">Network & Application</h4>
                    <div className="space-y-3">
                      <div className="rounded-lg border p-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-muted-foreground">Network In</span>
                          <span className="text-sm font-medium">{detailedMetrics.network?.traffic?.inbound_mbps || 0} Mbps</span>
                        </div>
                      </div>
                      <div className="rounded-lg border p-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-muted-foreground">Network Out</span>
                          <span className="text-sm font-medium">{detailedMetrics.network?.traffic?.outbound_mbps || 0} Mbps</span>
                        </div>
                      </div>
                      <div className="rounded-lg border p-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-muted-foreground">WebSocket Connections</span>
                          <span className="text-sm font-medium">{detailedMetrics.application?.websocket_connections || 0}</span>
                        </div>
                      </div>
                      <div className="rounded-lg border p-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-muted-foreground">Active Characters</span>
                          <span className="text-sm font-medium">{detailedMetrics.application?.characters_count || 0}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* System Info & Trends */}
                  <div className="space-y-4">
                    <h4 className="text-sm font-medium">System Info & Trends</h4>
                    <div className="space-y-3">
                      <div className="rounded-lg border p-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-muted-foreground">Platform</span>
                          <span className="text-sm font-medium">{detailedMetrics.system_info?.platform || "N/A"}</span>
                        </div>
                      </div>
                      <div className="rounded-lg border p-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-muted-foreground">Python Version</span>
                          <span className="text-sm font-medium">{detailedMetrics.system_info?.python_version || "N/A"}</span>
                        </div>
                      </div>
                      <div className="rounded-lg border p-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-muted-foreground">CPU Trend</span>
                          <span className="text-sm font-medium capitalize">{detailedMetrics.trends?.cpu_trend || "N/A"}</span>
                        </div>
                      </div>
                      <div className="rounded-lg border p-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-muted-foreground">Memory Trend</span>
                          <span className="text-sm font-medium capitalize">{detailedMetrics.trends?.memory_trend || "N/A"}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex h-40 flex-col items-center justify-center rounded-lg border border-dashed">
                  <XCircle className="h-10 w-10 text-muted-foreground" />
                  <h3 className="mt-4 text-lg font-medium">No Metrics Data</h3>
                  <p className="mt-2 text-sm text-muted-foreground">Unable to load detailed metrics information</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* System Information */}
          {(apiInfo || healthStatus) && (
            <Card>
              <CardHeader>
                <CardTitle>System Information</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-3">
                  {apiInfo && (
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium">API Information</h4>
                      <div className="space-y-1 text-sm text-muted-foreground">
                        <div>Service: {apiInfo.name}</div>
                        <div>Version: {apiInfo.version}</div>
                        <div>Description: {apiInfo.description}</div>
                      </div>
                    </div>
                  )}
                  
                  {healthStatus && (
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium">Service Health</h4>
                      <div className="space-y-1 text-sm text-muted-foreground">
                        <div>Services: {healthStatus.services ? Object.keys(healthStatus.services).length : 0}</div>
                        <div>Status: {healthStatus.system_overview?.status || "Unknown"}</div>
                        <div>Last updated: {healthStatus.system_overview?.last_updated || "Unknown"}</div>
                      </div>
                    </div>
                  )}

                  {detailedMetrics && (
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium">Application Stats</h4>
                      <div className="space-y-1 text-sm text-muted-foreground">
                        <div>Characters: {detailedMetrics.application?.characters_count || 0}</div>
                        <div>Active Conversations: {detailedMetrics.application?.active_conversations || 0}</div>
                        <div>Social Posts Today: {detailedMetrics.application?.social_posts_today || 0}</div>
                        <div>Uptime: {detailedMetrics.application?.uptime_seconds ? formatUptime(detailedMetrics.application.uptime_seconds) : "Unknown"}</div>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}