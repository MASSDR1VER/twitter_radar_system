"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { ExternalLink, Heart, Repeat2 } from "lucide-react"

interface MatchedPost {
  _id: string
  tweet_id: string
  username: string
  text: string
  created_at: string
  likes: number
  retweets: number
  url: string
  matched_keywords: string[]
  reply_status: "pending" | "replied" | "failed"
}

interface MatchedPostsProps {
  campaignId: string
}

export function MatchedPosts({ campaignId }: MatchedPostsProps) {
  const [posts, setPosts] = useState<MatchedPost[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<string | null>(null)

  useEffect(() => {
    fetchPosts()
  }, [campaignId, filter])

  const fetchPosts = async () => {
    try {
      setLoading(true)
      const url = new URL(`http://localhost:8000/api/v1/campaigns/${campaignId}/matched-posts`)
      if (filter) {
        url.searchParams.append("status", filter)
      }

      const response = await fetch(url.toString())
      const data = await response.json()

      if (data.success) {
        setPosts(data.posts)
        setTotal(data.total)
      }
    } catch (error) {
      console.error("Failed to fetch matched posts:", error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "pending":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
      case "replied":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
      case "failed":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200"
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Matched Posts</CardTitle>
            <CardDescription>
              {total} tweets found matching your keywords
            </CardDescription>
          </div>
          <div className="flex gap-2">
            <Button
              variant={filter === null ? "default" : "outline"}
              size="sm"
              onClick={() => setFilter(null)}
            >
              All
            </Button>
            <Button
              variant={filter === "pending" ? "default" : "outline"}
              size="sm"
              onClick={() => setFilter("pending")}
            >
              Pending
            </Button>
            <Button
              variant={filter === "replied" ? "default" : "outline"}
              size="sm"
              onClick={() => setFilter("replied")}
            >
              Replied
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex h-32 items-center justify-center text-muted-foreground">
            Loading...
          </div>
        ) : posts.length === 0 ? (
          <div className="flex h-32 items-center justify-center text-muted-foreground">
            No matched posts found
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>User</TableHead>
                <TableHead className="max-w-md">Tweet</TableHead>
                <TableHead>Keywords</TableHead>
                <TableHead>Engagement</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {posts.map((post) => (
                <TableRow key={post._id}>
                  <TableCell className="font-medium">
                    @{post.username}
                  </TableCell>
                  <TableCell className="max-w-md">
                    <p className="truncate text-sm">{post.text}</p>
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-1">
                      {post.matched_keywords.map((kw) => (
                        <Badge key={kw} variant="secondary" className="text-xs">
                          {kw}
                        </Badge>
                      ))}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-3 text-sm text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Heart className="h-3 w-3" />
                        {post.likes}
                      </span>
                      <span className="flex items-center gap-1">
                        <Repeat2 className="h-3 w-3" />
                        {post.retweets}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {formatDate(post.created_at)}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className={getStatusColor(post.reply_status)}>
                      {post.reply_status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => window.open(post.url, "_blank")}
                    >
                      <ExternalLink className="h-3 w-3" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  )
}
