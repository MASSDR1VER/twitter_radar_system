"use client"

import { useEffect, useState } from "react"
import { useRouter, useParams } from "next/navigation"
import { ArrowLeft, Play, Pause, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { CampaignLogs } from "@/components/campaign-logs"
import { MatchedPosts } from "@/components/matched-posts"

interface Campaign {
  _id: string
  name: string
  seed_users: string[]
  keywords: string[]
  status: string
  total_replies: number
  total_clicks: number
  daily_reply_limit: number
  dry_run: boolean
  ai_provider: string
  created_at: string
}

interface Analytics {
  total_replies: number
  total_clicks: number
  ctr: number
  engagement: {
    total_likes: number
    total_retweets: number
    total_replies: number
  }
  top_replies: Array<{
    tweet_id: string
    reply_text: string
    clicks: number
    likes: number
    retweets: number
  }>
  error_rate: number
}

export default function CampaignDetailPage() {
  const router = useRouter()
  const params = useParams()
  const campaignId = params.id as string

  const [campaign, setCampaign] = useState<Campaign | null>(null)
  const [analytics, setAnalytics] = useState<Analytics | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (campaignId) {
      fetchCampaignDetails()
      fetchAnalytics()
    }
  }, [campaignId])

  const fetchCampaignDetails = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/campaigns/${campaignId}`
      )
      const data = await response.json()
      setCampaign(data)
    } catch (error) {
      console.error("Failed to fetch campaign:", error)
    }
  }

  const fetchAnalytics = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/analytics/campaign/${campaignId}`
      )
      const data = await response.json()
      setAnalytics(data)
    } catch (error) {
      console.error("Failed to fetch analytics:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleToggleStatus = async () => {
    if (!campaign) return

    const endpoint =
      campaign.status === "active" ? "stop" : "start"

    try {
      await fetch(
        `http://localhost:8000/api/v1/campaigns/${campaignId}/${endpoint}`,
        { method: "POST" }
      )
      fetchCampaignDetails()
    } catch (error) {
      console.error(`Failed to ${endpoint} campaign:`, error)
    }
  }

  const handleRefresh = () => {
    setLoading(true)
    fetchCampaignDetails()
    fetchAnalytics()
  }

  if (loading || !campaign) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent"></div>
      </div>
    )
  }

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => router.push("/campaigns")}
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-3xl font-bold tracking-tight">
                {campaign.name}
              </h2>
              <Badge>{campaign.status}</Badge>
              {campaign.dry_run && (
                <Badge variant="outline">DRY RUN</Badge>
              )}
            </div>
            <p className="text-muted-foreground">Campaign details and analytics</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="icon" onClick={handleRefresh}>
            <RefreshCw className="h-4 w-4" />
          </Button>
          <Button onClick={handleToggleStatus}>
            {campaign.status === "active" ? (
              <>
                <Pause className="mr-2 h-4 w-4" />
                Pause Campaign
              </>
            ) : (
              <>
                <Play className="mr-2 h-4 w-4" />
                Start Campaign
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Replies</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics?.total_replies || 0}</div>
            <p className="text-xs text-muted-foreground">
              Limit: {campaign.daily_reply_limit}/day
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Clicks</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics?.total_clicks || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">CTR</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {analytics?.ctr ? `${analytics.ctr.toFixed(1)}%` : "0%"}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Error Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {analytics?.error_rate ? `${analytics.error_rate.toFixed(1)}%` : "0%"}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Live Logs - Show if campaign is active */}
      {campaign.status === "active" && (
        <CampaignLogs campaignId={params.id as string} />
      )}

      {/* Campaign Config */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Configuration</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div>
              <div className="text-sm font-medium">Seed Users</div>
              <div className="text-sm text-muted-foreground">
                {campaign.seed_users?.join(", ") || "N/A"}
              </div>
            </div>
            <div>
              <div className="text-sm font-medium">Keywords</div>
              <div className="text-sm text-muted-foreground">
                {campaign.keywords?.join(", ") || "N/A"}
              </div>
            </div>
            <div>
              <div className="text-sm font-medium">AI Provider</div>
              <div className="text-sm text-muted-foreground">
                {campaign.ai_provider || "openai"}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Engagement</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm font-medium">Likes</span>
              <span className="text-sm text-muted-foreground">
                {analytics?.engagement?.total_likes || 0}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm font-medium">Retweets</span>
              <span className="text-sm text-muted-foreground">
                {analytics?.engagement?.total_retweets || 0}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm font-medium">Replies</span>
              <span className="text-sm text-muted-foreground">
                {analytics?.engagement?.total_replies || 0}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Matched Posts */}
      <MatchedPosts campaignId={params.id as string} />

      {/* Top Replies */}
      <Card>
        <CardHeader>
          <CardTitle>Top Performing Replies</CardTitle>
          <CardDescription>Best replies by click-through rate</CardDescription>
        </CardHeader>
        <CardContent>
          {analytics?.top_replies && analytics.top_replies.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Reply</TableHead>
                  <TableHead>Clicks</TableHead>
                  <TableHead>Likes</TableHead>
                  <TableHead>Retweets</TableHead>
                  <TableHead>Links</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {analytics.top_replies.map((reply, index) => (
                  <TableRow key={index}>
                    <TableCell className="max-w-md truncate">
                      {reply.reply_text}
                    </TableCell>
                    <TableCell>{reply.clicks}</TableCell>
                    <TableCell>{reply.likes}</TableCell>
                    <TableCell>{reply.retweets}</TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        {reply.target_tweet_url && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => window.open(reply.target_tweet_url, '_blank')}
                          >
                            Original
                          </Button>
                        )}
                        {reply.reply_tweet_url && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => window.open(reply.reply_tweet_url, '_blank')}
                          >
                            Reply
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              No replies yet
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
