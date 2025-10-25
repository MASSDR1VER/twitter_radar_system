"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"

export default function NewCampaignPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    name: "",
    seed_users: "",
    top_n_users: 100,
    lookback_days: 7,
    keywords: "",
    use_grok_filter: false,
    target_url: "",
    reply_template: "",
    ai_provider: "openai",
    daily_reply_limit: 50,
    dry_run: true,
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const payload = {
        ...formData,
        seed_users: formData.seed_users.split(",").map((u) => u.trim()),
        keywords: formData.keywords.split(",").map((k) => k.trim()),
      }

      const response = await fetch("http://localhost:8000/api/v1/campaigns/create", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      })

      if (response.ok) {
        router.push("/campaigns")
      } else {
        const error = await response.json()
        alert(`Failed to create campaign: ${error.detail || "Unknown error"}`)
      }
    } catch (error) {
      console.error("Failed to create campaign:", error)
      alert("Failed to create campaign. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => router.push("/campaigns")}
        >
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h2 className="text-3xl font-bold tracking-tight">New Campaign</h2>
          <p className="text-muted-foreground">
            Create a new Twitter engagement campaign
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <Card>
          <CardHeader>
            <CardTitle>Campaign Details</CardTitle>
            <CardDescription>
              Configure your campaign settings
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Basic Info */}
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Campaign Name</Label>
                <Input
                  id="name"
                  required
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  placeholder="SaaS Founders Campaign"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="seed_users">
                  Seed Users (comma separated, with @)
                </Label>
                <Input
                  id="seed_users"
                  required
                  value={formData.seed_users}
                  onChange={(e) =>
                    setFormData({ ...formData, seed_users: e.target.value })
                  }
                  placeholder="@elonmusk, @sama, @pmarca"
                />
                <p className="text-xs text-muted-foreground">
                  Users to analyze for top interacted followers
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="top_n_users">Top N Users</Label>
                  <Input
                    id="top_n_users"
                    type="number"
                    required
                    value={formData.top_n_users}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        top_n_users: parseInt(e.target.value),
                      })
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="lookback_days">Lookback Days</Label>
                  <Input
                    id="lookback_days"
                    type="number"
                    required
                    value={formData.lookback_days}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        lookback_days: parseInt(e.target.value),
                      })
                    }
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="keywords">
                  Keywords (comma separated)
                </Label>
                <Input
                  id="keywords"
                  required
                  value={formData.keywords}
                  onChange={(e) =>
                    setFormData({ ...formData, keywords: e.target.value })
                  }
                  placeholder="startup, funding, SaaS, AI"
                />
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="use_grok_filter"
                  checked={formData.use_grok_filter}
                  onCheckedChange={(checked) =>
                    setFormData({ ...formData, use_grok_filter: checked })
                  }
                />
                <Label htmlFor="use_grok_filter">
                  Use Grok AI for tweet filtering
                </Label>
              </div>
            </div>

            {/* Reply Settings */}
            <div className="space-y-4 pt-4 border-t">
              <h3 className="text-lg font-semibold">Reply Settings</h3>

              <div className="space-y-2">
                <Label htmlFor="target_url">Target URL</Label>
                <Input
                  id="target_url"
                  type="url"
                  required
                  value={formData.target_url}
                  onChange={(e) =>
                    setFormData({ ...formData, target_url: e.target.value })
                  }
                  placeholder="https://yourproduct.com"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="reply_template">Reply Template</Label>
                <Textarea
                  id="reply_template"
                  required
                  value={formData.reply_template}
                  onChange={(e) =>
                    setFormData({ ...formData, reply_template: e.target.value })
                  }
                  placeholder="Great insights on {topic}! We're building something similar that might interest you: {link}"
                  rows={4}
                />
                <p className="text-xs text-muted-foreground">
                  Use {"{topic}"} and {"{link}"} as placeholders
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="ai_provider">AI Provider</Label>
                <Select
                  value={formData.ai_provider}
                  onValueChange={(value) =>
                    setFormData({ ...formData, ai_provider: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="openai">OpenAI (GPT-4)</SelectItem>
                    <SelectItem value="anthropic">Anthropic (Claude)</SelectItem>
                    <SelectItem value="grok">Grok AI (Twitter Native)</SelectItem>
                    <SelectItem value="both">Both (Grok + GPT-4/Claude)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="daily_reply_limit">Daily Reply Limit</Label>
                <Input
                  id="daily_reply_limit"
                  type="number"
                  required
                  value={formData.daily_reply_limit}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      daily_reply_limit: parseInt(e.target.value),
                    })
                  }
                />
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="dry_run"
                  checked={formData.dry_run}
                  onCheckedChange={(checked) =>
                    setFormData({ ...formData, dry_run: checked })
                  }
                />
                <Label htmlFor="dry_run">
                  Dry Run Mode (generate but don&apos;t post)
                </Label>
              </div>
            </div>

            <div className="flex gap-4 pt-4">
              <Button type="submit" disabled={loading}>
                {loading ? "Creating..." : "Create Campaign"}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => router.push("/campaigns")}
              >
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  )
}
