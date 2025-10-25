"use client"

import { useState } from "react"
import {
  AlertCircle,
  Check,
  ChevronDown,
  Clock,
  Download,
  ExternalLink,
  Filter,
  MoreHorizontal,
  RefreshCw,
  Search,
  Settings,
  XCircle,
} from "lucide-react"
import Link from "next/link"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { DashboardHeader } from "@/components/dashboard-header"

// Mock data for API endpoints
const apiEndpoints = [
  {
    id: "api-1",
    name: "Character API",
    status: "operational",
    uptime: 99.98,
    responseTime: 120, // ms
    requests: 15420,
    errors: 3,
    lastChecked: "2023-06-15T10:30:00Z",
  },
  {
    id: "api-2",
    name: "Conversation API",
    status: "operational",
    uptime: 99.95,
    responseTime: 150, // ms
    requests: 8750,
    errors: 5,
    lastChecked: "2023-06-15T10:30:00Z",
  },
  {
    id: "api-3",
    name: "Knowledge API",
    status: "degraded",
    uptime: 98.75,
    responseTime: 320, // ms
    requests: 4230,
    errors: 28,
    lastChecked: "2023-06-15T10:30:00Z",
  },
  {
    id: "api-4",
    name: "Social Media API",
    status: "operational",
    uptime: 99.9,
    responseTime: 180, // ms
    requests: 6120,
    errors: 8,
    lastChecked: "2023-06-15T10:30:00Z",
  },
  {
    id: "api-5",
    name: "Analytics API",
    status: "operational",
    uptime: 99.99,
    responseTime: 90, // ms
    requests: 3450,
    errors: 1,
    lastChecked: "2023-06-15T10:30:00Z",
  },
  {
    id: "api-6",
    name: "External Integration API",
    status: "outage",
    uptime: 95.2,
    responseTime: 500, // ms
    requests: 1820,
    errors: 124,
    lastChecked: "2023-06-15T10:30:00Z",
  },
]

// Mock data for recent incidents
const recentIncidents = [
  {
    id: "incident-1",
    title: "External Integration API Outage",
    status: "investigating",
    startedAt: "2023-06-15T09:45:00Z",
    resolvedAt: null,
    affectedServices: ["External Integration API"],
    updates: [
      {
        timestamp: "2023-06-15T09:45:00Z",
        message: "We are investigating issues with the External Integration API.",
        status: "investigating",
      },
      {
        timestamp: "2023-06-15T10:00:00Z",
        message: "The issue has been identified as a connection problem with the third-party service.",
        status: "identified",
      },
    ],
  },
  {
    id: "incident-2",
    title: "Knowledge API Performance Degradation",
    status: "monitoring",
    startedAt: "2023-06-15T08:30:00Z",
    resolvedAt: null,
    affectedServices: ["Knowledge API"],
    updates: [
      {
        timestamp: "2023-06-15T08:30:00Z",
        message: "We are investigating slow response times from the Knowledge API.",
        status: "investigating",
      },
      {
        timestamp: "2023-06-15T08:45:00Z",
        message: "The issue has been identified as high database load.",
        status: "identified",
      },
      {
        timestamp: "2023-06-15T09:15:00Z",
        message: "We have implemented a fix and are monitoring the situation.",
        status: "monitoring",
      },
    ],
  },
  {
    id: "incident-3",
    title: "Character API Brief Outage",
    status: "resolved",
    startedAt: "2023-06-14T14:20:00Z",
    resolvedAt: "2023-06-14T14:50:00Z",
    affectedServices: ["Character API"],
    updates: [
      {
        timestamp: "2023-06-14T14:20:00Z",
        message: "We are investigating issues with the Character API.",
        status: "investigating",
      },
      {
        timestamp: "2023-06-14T14:35:00Z",
        message: "The issue has been identified as a server overload.",
        status: "identified",
      },
      {
        timestamp: "2023-06-14T14:50:00Z",
        message: "The issue has been resolved and the service is back to normal.",
        status: "resolved",
      },
    ],
  },
]

export default function ApiStatusPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedStatus, setSelectedStatus] = useState<string>("all")
  const [activeTab, setActiveTab] = useState("overview")
  const [isRefreshing, setIsRefreshing] = useState(false)

  // Filter API endpoints based on search query and filters
  const filteredEndpoints = apiEndpoints.filter(
    (endpoint) =>
      endpoint.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
      (selectedStatus === "all" || endpoint.status === selectedStatus),
  )

  const handleRefresh = () => {
    setIsRefreshing(true)
    // Simulate refresh
    setTimeout(() => {
      setIsRefreshing(false)
    }, 1000)
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "operational":
        return (
          <Badge variant="outline" className="border-green-500 text-green-500 capitalize">
            <Check className="mr-1 h-3 w-3" />
            {status}
          </Badge>
        )
      case "degraded":
        return (
          <Badge variant="outline" className="border-amber-500 text-amber-500 capitalize">
            <AlertCircle className="mr-1 h-3 w-3" />
            {status}
          </Badge>
        )
      case "outage":
        return (
          <Badge variant="destructive" className="capitalize">
            <XCircle className="mr-1 h-3 w-3" />
            {status}
          </Badge>
        )
      default:
        return (
          <Badge variant="outline" className="capitalize">
            {status}
          </Badge>
        )
    }
  }

  const getIncidentStatusBadge = (status: string) => {
    switch (status) {
      case "investigating":
        return (
          <Badge variant="destructive" className="capitalize">
            <AlertCircle className="mr-1 h-3 w-3" />
            {status}
          </Badge>
        )
      case "identified":
        return (
          <Badge variant="outline" className="border-amber-500 text-amber-500 capitalize">
            <Search className="mr-1 h-3 w-3" />
            {status}
          </Badge>
        )
      case "monitoring":
        return (
          <Badge variant="outline" className="border-blue-500 text-blue-500 capitalize">
            <Clock className="mr-1 h-3 w-3" />
            {status}
          </Badge>
        )
      case "resolved":
        return (
          <Badge variant="outline" className="border-green-500 text-green-500 capitalize">
            <Check className="mr-1 h-3 w-3" />
            {status}
          </Badge>
        )
      default:
        return (
          <Badge variant="outline" className="capitalize">
            {status}
          </Badge>
        )
    }
  }

  return (
    <div className="flex flex-col w-full">
      <DashboardHeader 
        breadcrumbs={[
          { title: "System", href: "/system" },
          { title: "API Status" }
        ]}
      >
        <Button variant="outline" size="sm" className="h-8 gap-1" onClick={handleRefresh} disabled={isRefreshing}>
          <RefreshCw className={`h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
          <span>{isRefreshing ? "Refreshing..." : "Refresh"}</span>
        </Button>
        <Button variant="outline" size="sm" className="h-8 gap-1">
          <Download className="h-4 w-4" />
          <span>Export</span>
        </Button>
        <Button variant="outline" size="icon" className="h-8 w-8">
          <Settings className="h-4 w-4" />
          <span className="sr-only">Settings</span>
        </Button>
      </DashboardHeader>

      <div className="flex-1 p-4 md:p-6">
        <div className="mx-auto max-w-6xl space-y-6">

          <div className="grid gap-6 md:grid-cols-4">
            <Card className="md:col-span-1">
              <CardHeader className="pb-3">
                <CardTitle>System Status</CardTitle>
                <CardDescription>Current system health</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Overall Status</span>
                    {apiEndpoints.some((endpoint) => endpoint.status === "outage") ? (
                      <Badge variant="destructive">
                        <XCircle className="mr-1 h-3 w-3" />
                        Major Outage
                      </Badge>
                    ) : apiEndpoints.some((endpoint) => endpoint.status === "degraded") ? (
                      <Badge variant="outline" className="border-amber-500 text-amber-500">
                        <AlertCircle className="mr-1 h-3 w-3" />
                        Partial Outage
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="border-green-500 text-green-500">
                        <Check className="mr-1 h-3 w-3" />
                        All Systems Operational
                      </Badge>
                    )}
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Operational</span>
                    <Badge variant="outline" className="border-green-500 text-green-500">
                      {apiEndpoints.filter((endpoint) => endpoint.status === "operational").length} /{" "}
                      {apiEndpoints.length}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Degraded</span>
                    <Badge variant="outline" className="border-amber-500 text-amber-500">
                      {apiEndpoints.filter((endpoint) => endpoint.status === "degraded").length} / {apiEndpoints.length}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Outage</span>
                    <Badge variant="outline" className="border-destructive text-destructive">
                      {apiEndpoints.filter((endpoint) => endpoint.status === "outage").length} / {apiEndpoints.length}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Last Updated</span>
                    <span className="text-sm text-muted-foreground">
                      {new Date().toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </span>
                  </div>
                </div>
              </CardContent>
              <CardFooter>
                <Button variant="outline" className="w-full" asChild>
                  <a href="https://status.example.com" target="_blank" rel="noopener noreferrer">
                    <ExternalLink className="mr-2 h-4 w-4" />
                    Status Page
                  </a>
                </Button>
              </CardFooter>
            </Card>

            <Card className="md:col-span-3">
              <CardHeader className="pb-3">
                <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <CardTitle>Active Incidents</CardTitle>
                    <CardDescription>
                      {recentIncidents.filter((incident) => incident.status !== "resolved").length} active{" "}
                      {recentIncidents.filter((incident) => incident.status !== "resolved").length === 1
                        ? "incident"
                        : "incidents"}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentIncidents
                    .filter((incident) => incident.status !== "resolved")
                    .map((incident) => (
                      <Card key={incident.id}>
                        <CardHeader className="p-4 pb-2">
                          <div className="flex items-start justify-between">
                            <div>
                              <CardTitle className="text-base">{incident.title}</CardTitle>
                              <CardDescription>
                                Started{" "}
                                {new Date(incident.startedAt).toLocaleString([], {
                                  dateStyle: "medium",
                                  timeStyle: "short",
                                })}
                              </CardDescription>
                            </div>
                            {getIncidentStatusBadge(incident.status)}
                          </div>
                        </CardHeader>
                        <CardContent className="p-4 pt-0">
                          <div className="space-y-2">
                            <div>
                              <span className="text-sm font-medium">Affected Services:</span>
                              <div className="mt-1 flex flex-wrap gap-1">
                                {incident.affectedServices.map((service, index) => (
                                  <Badge key={index} variant="outline">
                                    {service}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                            <div>
                              <span className="text-sm font-medium">Updates:</span>
                              <div className="mt-1 space-y-2">
                                {incident.updates.map((update, index) => (
                                  <div key={index} className="rounded-md bg-muted p-2 text-sm">
                                    <div className="flex items-center justify-between">
                                      <span className="font-medium capitalize">{update.status}</span>
                                      <span className="text-xs text-muted-foreground">
                                        {new Date(update.timestamp).toLocaleString([], {
                                          dateStyle: "medium",
                                          timeStyle: "short",
                                        })}
                                      </span>
                                    </div>
                                    <p className="mt-1">{update.message}</p>
                                  </div>
                                ))}
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}

                  {recentIncidents.filter((incident) => incident.status !== "resolved").length === 0 && (
                    <div className="flex flex-col items-center justify-center rounded-lg border border-dashed p-8 text-center">
                      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-green-500/10">
                        <Check className="h-6 w-6 text-green-500" />
                      </div>
                      <h3 className="mt-4 text-lg font-medium">All Systems Operational</h3>
                      <p className="mt-2 text-sm text-muted-foreground">There are no active incidents at this time.</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <div className="flex flex-col gap-4 md:flex-row md:items-center">
              <TabsList>
                <TabsTrigger value="overview">API Overview</TabsTrigger>
                <TabsTrigger value="incidents">Incident History</TabsTrigger>
              </TabsList>
              {activeTab === "overview" && (
                <div className="flex flex-1 flex-col gap-2 md:flex-row">
                  <div className="relative flex-1">
                    <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search APIs..."
                      className="pl-8"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                    />
                  </div>
                  <div className="flex gap-2">
                    <Select value={selectedStatus} onValueChange={setSelectedStatus}>
                      <SelectTrigger className="w-full md:w-[180px]">
                        <SelectValue placeholder="All Status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Status</SelectItem>
                        <SelectItem value="operational">Operational</SelectItem>
                        <SelectItem value="degraded">Degraded</SelectItem>
                        <SelectItem value="outage">Outage</SelectItem>
                      </SelectContent>
                    </Select>
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button variant="outline" size="sm" className="h-9 gap-1">
                          <Filter className="h-4 w-4" />
                          <span>Filter</span>
                          <ChevronDown className="h-4 w-4" />
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-[200px] p-0" align="end">
                        <div className="p-2">
                          <div className="space-y-2">
                            <div className="font-medium">Response Time</div>
                            <div className="flex items-center space-x-2">
                              <input type="checkbox" id="response-fast" className="h-4 w-4" defaultChecked />
                              <label htmlFor="response-fast" className="text-sm">
                                Fast (&lt; 100ms)
                              </label>
                            </div>
                            <div className="flex items-center space-x-2">
                              <input type="checkbox" id="response-medium" className="h-4 w-4" defaultChecked />
                              <label htmlFor="response-medium" className="text-sm">
                                Medium (100-300ms)
                              </label>
                            </div>
                            <div className="flex items-center space-x-2">
                              <input type="checkbox" id="response-slow" className="h-4 w-4" defaultChecked />
                              <label htmlFor="response-slow" className="text-sm">
                                Slow (&gt; 300ms)
                              </label>
                            </div>
                          </div>
                          <div className="mt-4 space-y-2">
                            <div className="font-medium">Error Rate</div>
                            <div className="flex items-center space-x-2">
                              <input type="checkbox" id="error-low" className="h-4 w-4" defaultChecked />
                              <label htmlFor="error-low" className="text-sm">
                                Low (&lt; 0.1%)
                              </label>
                            </div>
                            <div className="flex items-center space-x-2">
                              <input type="checkbox" id="error-medium" className="h-4 w-4" defaultChecked />
                              <label htmlFor="error-medium" className="text-sm">
                                Medium (0.1-1%)
                              </label>
                            </div>
                            <div className="flex items-center space-x-2">
                              <input type="checkbox" id="error-high" className="h-4 w-4" defaultChecked />
                              <label htmlFor="error-high" className="text-sm">
                                High (&gt; 1%)
                              </label>
                            </div>
                          </div>
                          <div className="mt-4 flex items-center justify-between">
                            <Button variant="ghost" size="sm">
                              Reset
                            </Button>
                            <Button size="sm">Apply</Button>
                          </div>
                        </div>
                      </PopoverContent>
                    </Popover>
                  </div>
                </div>
              )}
            </div>

            <TabsContent value="overview" className="mt-6">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle>API Endpoints</CardTitle>
                  <CardDescription>
                    {filteredEndpoints.length} API {filteredEndpoints.length === 1 ? "endpoint" : "endpoints"} found
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>API Name</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Uptime</TableHead>
                          <TableHead>Response Time</TableHead>
                          <TableHead>Requests (24h)</TableHead>
                          <TableHead>Error Rate</TableHead>
                          <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {filteredEndpoints.length === 0 ? (
                          <TableRow>
                            <TableCell colSpan={7} className="h-24 text-center">
                              No API endpoints found.
                            </TableCell>
                          </TableRow>
                        ) : (
                          filteredEndpoints.map((endpoint) => (
                            <TableRow key={endpoint.id}>
                              <TableCell className="font-medium">{endpoint.name}</TableCell>
                              <TableCell>{getStatusBadge(endpoint.status)}</TableCell>
                              <TableCell>{endpoint.uptime.toFixed(2)}%</TableCell>
                              <TableCell>
                                <div className="flex items-center gap-2">
                                  <span
                                    className={
                                      endpoint.responseTime < 100
                                        ? "text-green-500"
                                        : endpoint.responseTime < 300
                                          ? "text-amber-500"
                                          : "text-destructive"
                                    }
                                  >
                                    {endpoint.responseTime} ms
                                  </span>
                                </div>
                              </TableCell>
                              <TableCell>{endpoint.requests.toLocaleString()}</TableCell>
                              <TableCell>
                                <div className="flex items-center gap-2">
                                  <span
                                    className={
                                      (endpoint.errors / endpoint.requests) * 100 < 0.1
                                        ? "text-green-500"
                                        : (endpoint.errors / endpoint.requests) * 100 < 1
                                          ? "text-amber-500"
                                          : "text-destructive"
                                    }
                                  >
                                    {((endpoint.errors / endpoint.requests) * 100).toFixed(2)}%
                                  </span>
                                  <span className="text-xs text-muted-foreground">({endpoint.errors})</span>
                                </div>
                              </TableCell>
                              <TableCell className="text-right">
                                <DropdownMenu>
                                  <DropdownMenuTrigger asChild>
                                    <Button variant="ghost" size="icon" className="h-8 w-8">
                                      <MoreHorizontal className="h-4 w-4" />
                                      <span className="sr-only">More options</span>
                                    </Button>
                                  </DropdownMenuTrigger>
                                  <DropdownMenuContent align="end">
                                    <DropdownMenuItem>View Details</DropdownMenuItem>
                                    <DropdownMenuItem>View Logs</DropdownMenuItem>
                                    <DropdownMenuItem>Test Endpoint</DropdownMenuItem>
                                  </DropdownMenuContent>
                                </DropdownMenu>
                              </TableCell>
                            </TableRow>
                          ))
                        )}
                      </TableBody>
                    </Table>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="incidents" className="mt-6">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle>Incident History</CardTitle>
                  <CardDescription>
                    {recentIncidents.length} recent {recentIncidents.length === 1 ? "incident" : "incidents"}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {recentIncidents.map((incident) => (
                      <Card key={incident.id}>
                        <CardHeader className="p-4 pb-2">
                          <div className="flex items-start justify-between">
                            <div>
                              <CardTitle className="text-base">{incident.title}</CardTitle>
                              <CardDescription>
                                {incident.resolvedAt
                                  ? `${new Date(incident.startedAt).toLocaleDateString()} - ${new Date(
                                      incident.resolvedAt,
                                    ).toLocaleDateString()}`
                                  : `Started ${new Date(incident.startedAt).toLocaleDateString()}`}
                              </CardDescription>
                            </div>
                            {getIncidentStatusBadge(incident.status)}
                          </div>
                        </CardHeader>
                        <CardContent className="p-4 pt-0">
                          <div className="space-y-2">
                            <div>
                              <span className="text-sm font-medium">Affected Services:</span>
                              <div className="mt-1 flex flex-wrap gap-1">
                                {incident.affectedServices.map((service, index) => (
                                  <Badge key={index} variant="outline">
                                    {service}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                            <div>
                              <span className="text-sm font-medium">Timeline:</span>
                              <div className="mt-1 space-y-2">
                                {incident.updates.map((update, index) => (
                                  <div key={index} className="rounded-md bg-muted p-2 text-sm">
                                    <div className="flex items-center justify-between">
                                      <span className="font-medium capitalize">{update.status}</span>
                                      <span className="text-xs text-muted-foreground">
                                        {new Date(update.timestamp).toLocaleString([], {
                                          dateStyle: "medium",
                                          timeStyle: "short",
                                        })}
                                      </span>
                                    </div>
                                    <p className="mt-1">{update.message}</p>
                                  </div>
                                ))}
                              </div>
                            </div>
                            {incident.resolvedAt && (
                              <div>
                                <span className="text-sm font-medium">Resolution Time:</span>
                                <div className="mt-1 text-sm">
                                  {Math.round(
                                    (new Date(incident.resolvedAt).getTime() - new Date(incident.startedAt).getTime()) /
                                      (1000 * 60),
                                  )}{" "}
                                  minutes
                                </div>
                              </div>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  )
}
