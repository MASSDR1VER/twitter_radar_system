"use client"

import { useEffect, useState } from "react"
import { Plus, Play, Pause, Trash2, Eye } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { useRouter } from "next/navigation"

interface Campaign {
  id: string
  name: string
  seed_users: string[]
  keywords: string[]
  status: "draft" | "active" | "paused" | "completed"
  total_replies: number
  total_clicks: number
  daily_reply_limit: number
  dry_run: boolean
  ai_provider?: string
  created_at: string
}

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    fetchCampaigns()
  }, [])

  const fetchCampaigns = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/campaigns")
      const data = await response.json()
      setCampaigns(data.campaigns || [])
    } catch (error) {
      console.error("Failed to fetch campaigns:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleStart = async (id: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/campaigns/${id}/start`, {
        method: "POST",
      })
      const data = await response.json()

      if (!data.success) {
        alert(data.error || "Failed to start campaign")
        return
      }

      fetchCampaigns()
    } catch (error) {
      console.error("Failed to start campaign:", error)
      alert("Failed to start campaign. Please try again.")
    }
  }

  const handleStop = async (id: string) => {
    try {
      await fetch(`http://localhost:8000/api/v1/campaigns/${id}/stop`, {
        method: "POST",
      })
      fetchCampaigns()
    } catch (error) {
      console.error("Failed to stop campaign:", error)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this campaign?")) return

    try {
      await fetch(`http://localhost:8000/api/v1/campaigns/${id}`, {
        method: "DELETE",
      })
      fetchCampaigns()
    } catch (error) {
      console.error("Failed to delete campaign:", error)
    }
  }

  const getStatusBadge = (status: string) => {
    const variants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
      draft: "secondary",
      active: "default",
      paused: "outline",
      completed: "destructive",
    }
    return <Badge variant={variants[status] || "default"}>{status}</Badge>
  }

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Campaigns</h2>
          <p className="text-muted-foreground">
            Manage your Twitter engagement campaigns
          </p>
        </div>
        <Button onClick={() => router.push("/campaigns/new")}>
          <Plus className="mr-2 h-4 w-4" />
          New Campaign
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Campaigns</CardTitle>
          <CardDescription>
            View and manage your active campaigns
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center py-8">
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent"></div>
            </div>
          ) : campaigns.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No campaigns yet. Create your first campaign to get started.
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Seed Users</TableHead>
                  <TableHead>Keywords</TableHead>
                  <TableHead>Replies</TableHead>
                  <TableHead>Clicks</TableHead>
                  <TableHead>CTR</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {campaigns.map((campaign) => (
                  <TableRow key={campaign.id}>
                    <TableCell className="font-medium">
                      {campaign.name}
                      {campaign.dry_run && (
                        <Badge variant="outline" className="ml-2">DRY RUN</Badge>
                      )}
                    </TableCell>
                    <TableCell>{getStatusBadge(campaign.status)}</TableCell>
                    <TableCell>
                      {campaign.seed_users.slice(0, 2).join(", ")}
                      {campaign.seed_users.length > 2 && ` +${campaign.seed_users.length - 2}`}
                    </TableCell>
                    <TableCell>
                      {campaign.keywords.slice(0, 2).join(", ")}
                      {campaign.keywords.length > 2 && ` +${campaign.keywords.length - 2}`}
                    </TableCell>
                    <TableCell>{campaign.total_replies}</TableCell>
                    <TableCell>{campaign.total_clicks}</TableCell>
                    <TableCell>
                      {campaign.total_replies > 0
                        ? `${((campaign.total_clicks / campaign.total_replies) * 100).toFixed(1)}%`
                        : "0%"}
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => router.push(`/campaigns/${campaign.id}`)}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        {campaign.status === "active" ? (
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleStop(campaign.id)}
                          >
                            <Pause className="h-4 w-4" />
                          </Button>
                        ) : (
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleStart(campaign.id)}
                          >
                            <Play className="h-4 w-4" />
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleDelete(campaign.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
