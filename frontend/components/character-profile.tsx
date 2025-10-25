"use client"

import { useState, useEffect } from "react"
import { Edit, Globe, MessageSquare, MoreHorizontal, Share2, Trash2, Twitter } from "lucide-react"
import Link from "next/link"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { CharacterPersonalityChart } from "@/components/character-personality-chart"
import { CharacterActivityChart } from "@/components/character-activity-chart"
import { CharacterKnowledgeList } from "@/components/character-knowledge-list"
import { CharacterConversationList } from "@/components/character-conversation-list"
import { CharacterSocialPosts } from "@/components/character-social-posts"
import { DashboardHeader } from "@/components/dashboard-header"
import { api } from "@/lib/api"
import { useAuth } from "@/contexts/auth-context"
import { Skeleton } from "@/components/ui/skeleton"

interface CharacterData {
  id: string
  name: string
  bio: {
    name: string
    age: number
    occupation: string
    education: string
    location: string
    interests: string[]
  }
  personality: Record<string, number>
  summary: string
  created_at: string
  last_updated: string
  is_public: boolean
  is_active: boolean
  stats: {
    total_conversations: number
    total_messages: number
    social_posts: number
    knowledge_items: number
  }
  social_platforms: string[]
  social_accounts: Array<{
    platform: string
    connected_at: string
    username: string
    user_id: string
    display_name: string
    profile_image_url: string
    bio: string
    location: string
    url: string
    created_at: string
    verified: boolean
    followers_count: number
    following_count: number
    profile_banner_url?: string
    is_active: boolean
  }>
  knowledge_base: Array<{
    content: string
    importance: number
    tags: string[]
    source: string
    created: string
  }>
  recent_conversations: Array<{
    id: string
    last_message: string | null
    message_count: number
    status: string
    started: string
    last_updated: string
  }>
  social_posts: any[]
  activity_chart_data: Array<{
    date: string
    chat_messages: number
    social_posts: number
  }>
}

export function CharacterProfile({ characterId }: { characterId: string }) {
  const [activeTab, setActiveTab] = useState("overview")
  const [characterData, setCharacterData] = useState<CharacterData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { isAuthenticated } = useAuth()

  useEffect(() => {
    const fetchCharacter = async () => {
      if (!isAuthenticated) {
        setIsLoading(false)
        return
      }

      try {
        const response = await api.getCharacter(characterId)
        if (response.success && response.data) {
          setCharacterData(response.data)
        } else {
          setError(response.error || 'Failed to load character')
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred')
      } finally {
        setIsLoading(false)
      }
    }

    fetchCharacter()
  }, [characterId, isAuthenticated])

  if (isLoading) {
    return (
      <div className="flex flex-col w-full">
        <DashboardHeader 
          breadcrumbs={[
            { title: "Characters", href: "/characters" },
            { title: "Loading..." }
          ]}
        />
        <div className="flex flex-col gap-6 p-4 md:p-6">
          <div className="flex flex-col md:flex-row gap-6">
            <div className="flex flex-col items-center md:items-start gap-4 md:flex-row">
              <Skeleton className="h-20 w-20 rounded-full" />
              <div className="flex flex-col gap-2">
                <Skeleton className="h-8 w-48" />
                <Skeleton className="h-4 w-32" />
              </div>
            </div>
          </div>
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    )
  }

  if (error || !characterData) {
    return (
      <div className="flex flex-col w-full">
        <DashboardHeader 
          breadcrumbs={[
            { title: "Characters", href: "/characters" },
            { title: "Error" }
          ]}
        />
        <div className="flex flex-col gap-6 p-4 md:p-6">
          <Card>
            <CardContent className="pt-6">
              <div className="text-center text-red-600 dark:text-red-400">
                {error || 'Character not found'}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col w-full">
      <DashboardHeader 
        breadcrumbs={[
          { title: "Characters", href: "/characters" },
          { title: characterData.name }
        ]}
      >
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="h-8 gap-1">
            <MessageSquare className="h-4 w-4" />
            <span>Chat</span>
          </Button>
          <Button variant="outline" size="sm" className="h-8 gap-1">
            <Edit className="h-4 w-4" />
            <span>Edit</span>
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <MoreHorizontal className="h-4 w-4" />
                <span className="sr-only">More options</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem>
                <Share2 className="mr-2 h-4 w-4" />
                <span>Share Character</span>
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Globe className="mr-2 h-4 w-4" />
                <span>Make {characterData.is_public ? "Private" : "Public"}</span>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-destructive">
                <Trash2 className="mr-2 h-4 w-4" />
                <span>Delete Character</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </DashboardHeader>

      <div className="flex flex-col gap-6 p-4 md:p-6">
        <div className="flex flex-col md:flex-row gap-6">
          <div className="flex flex-col items-center md:items-start gap-4 md:flex-row">
            <Avatar className="h-20 w-20">
              <AvatarImage
                src={`https://api.dicebear.com/7.x/personas/svg?seed=${characterData.name}`}
                alt={characterData.name}
              />
              <AvatarFallback>{characterData.name.substring(0, 2).toUpperCase()}</AvatarFallback>
            </Avatar>
            <div className="flex flex-col items-center md:items-start gap-2">
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold">{characterData.name}</h1>
                <Badge variant={characterData.is_active ? "default" : "outline"}>
                  {characterData.is_active ? "Active" : "Inactive"}
                </Badge>
                <Badge variant={characterData.is_public ? "secondary" : "outline"}>
                  {characterData.is_public ? "Public" : "Private"}
                </Badge>
              </div>
              <div className="text-muted-foreground text-sm">
                {characterData.bio.occupation} • {characterData.bio.location}
              </div>
              <div className="flex gap-2 mt-1">
                {characterData.social_platforms && characterData.social_platforms.length > 0 && (
                  characterData.social_platforms.map((platform) => (
                    <Badge key={platform} variant="outline" className="text-xs">
                      {platform}
                    </Badge>
                  ))
                )}
              </div>
            </div>
          </div>

          <div className="flex gap-2 ml-auto mt-4 md:mt-0">
            <Card className="w-full md:w-auto">
              <CardHeader className="p-3">
                <CardDescription>Conversations</CardDescription>
                <CardTitle className="text-base">{characterData.stats.total_conversations}</CardTitle>
              </CardHeader>
            </Card>
            <Card className="w-full md:w-auto">
              <CardHeader className="p-3">
                <CardDescription>Messages</CardDescription>
                <CardTitle className="text-base">{characterData.stats.total_messages}</CardTitle>
              </CardHeader>
            </Card>
            <Card className="w-full md:w-auto">
              <CardHeader className="p-3">
                <CardDescription>Knowledge Items</CardDescription>
                <CardTitle className="text-base">{characterData.stats.knowledge_items}</CardTitle>
              </CardHeader>
            </Card>
          </div>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid grid-cols-5 md:w-fit">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="personality">Personality</TabsTrigger>
            <TabsTrigger value="knowledge">Knowledge</TabsTrigger>
            <TabsTrigger value="conversations">Conversations</TabsTrigger>
            <TabsTrigger value="social">Social</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="mt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Bio</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-4">
                    <div className="grid grid-cols-2 gap-2">
                      <div className="text-sm font-medium">Age</div>
                      <div className="text-sm">{characterData.bio.age}</div>
                      <div className="text-sm font-medium">Occupation</div>
                      <div className="text-sm">{characterData.bio.occupation}</div>
                      <div className="text-sm font-medium">Education</div>
                      <div className="text-sm">{characterData.bio.education}</div>
                      <div className="text-sm font-medium">Location</div>
                      <div className="text-sm">{characterData.bio.location}</div>
                    </div>
                    <Separator />
                    <div>
                      <div className="text-sm font-medium mb-2">Interests</div>
                      <div className="flex flex-wrap gap-2">
                        {characterData.bio.interests.map((interest) => (
                          <Badge key={interest} variant="secondary">
                            {interest}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-sm text-muted-foreground whitespace-pre-line">
                    {characterData.summary}
                  </div>
                  <Separator className="my-4" />
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="font-medium">Created</div>
                    <div>{new Date(characterData.created_at).toLocaleDateString()}</div>
                    <div className="font-medium">Last Updated</div>
                    <div>{new Date(characterData.last_updated).toLocaleDateString()}</div>
                  </div>
                </CardContent>
              </Card>

              <Card className="md:col-span-2">
                <CardHeader>
                  <CardTitle>Recent Activity</CardTitle>
                </CardHeader>
                <CardContent>
                  <CharacterActivityChart data={characterData.activity_chart_data} />
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="personality" className="mt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {typeof characterData.personality === 'object' && characterData.personality !== null ? (
                <>
                  <Card>
                    <CardHeader>
                      <CardTitle>Personality Traits</CardTitle>
                    </CardHeader>
                    <CardContent className="h-[350px]">
                      <CharacterPersonalityChart personality={characterData.personality} />
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle>Personality Details</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {Object.entries(characterData.personality).map(([trait, value]) => (
                          <div key={trait} className="space-y-1">
                            <div className="flex items-center justify-between">
                              <span className="text-sm font-medium capitalize">{trait}</span>
                              <span className="text-sm text-muted-foreground">
                                {typeof value === 'number' ? `${value}/10` : String(value)}
                              </span>
                            </div>
                            {typeof value === 'number' && (
                              <div className="h-2 rounded-full bg-secondary overflow-hidden">
                                <div className="h-full bg-primary" style={{ width: `${(value / 10) * 100}%` }} />
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </>
              ) : (
                <Card className="md:col-span-2">
                  <CardHeader>
                    <CardTitle>Personality</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-center py-8">
                      <p className="text-muted-foreground">
                        {typeof characterData.personality === 'string' 
                          ? characterData.personality 
                          : 'No personality data available'
                        }
                      </p>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          <TabsContent value="knowledge" className="mt-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Knowledge Base ({characterData.knowledge_base.length} items)</CardTitle>
                <Button size="sm">Add Knowledge</Button>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {characterData.knowledge_base.length > 0 ? (
                    characterData.knowledge_base.slice(0, 10).map((item, index) => (
                      <div key={index} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <Badge variant="outline">Importance: {item.importance}/10</Badge>
                            {item.tags.map((tag) => (
                              <Badge key={tag} variant="secondary" className="text-xs">
                                {tag}
                              </Badge>
                            ))}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {new Date(item.created).toLocaleDateString()}
                          </div>
                        </div>
                        <p className="text-sm text-muted-foreground line-clamp-3">
                          {item.content}
                        </p>
                        <div className="mt-2 text-xs text-muted-foreground">
                          Source: {item.source}
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      No knowledge items yet
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="conversations" className="mt-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Recent Conversations ({characterData.recent_conversations.length})</CardTitle>
                <Button asChild size="sm">
                  <Link href={`/chat?character=${characterId}`}>Start New Conversation</Link>
                </Button>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {characterData.recent_conversations.length > 0 ? (
                    characterData.recent_conversations.map((conversation) => (
                      <div key={conversation.id} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <Badge variant={conversation.status === 'Active' ? 'default' : 'outline'}>
                              {conversation.status}
                            </Badge>
                            <span className="text-sm text-muted-foreground">
                              {conversation.message_count} messages
                            </span>
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {new Date(conversation.last_updated).toLocaleDateString()}
                          </div>
                        </div>
                        {conversation.last_message && (
                          <p className="text-sm text-muted-foreground line-clamp-2">
                            {conversation.last_message}
                          </p>
                        )}
                        <div className="mt-2 text-xs text-muted-foreground">
                          Started: {new Date(conversation.started).toLocaleString()}
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      No conversations yet
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="social" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Connected Social Accounts ({characterData.social_accounts?.length || 0})</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {characterData.social_accounts && characterData.social_accounts.length > 0 ? (
                    characterData.social_accounts.map((account, index) => (
                      <div key={index} className="border rounded-lg p-6">
                        <div className="flex items-start gap-6">
                          <Avatar className="h-16 w-16">
                            <AvatarImage src={account.profile_image_url} alt={account.display_name} />
                            <AvatarFallback>
                              {account.platform === 'twitter' ? <Twitter className="h-8 w-8" /> : account.platform.charAt(0).toUpperCase()}
                            </AvatarFallback>
                          </Avatar>
                          <div className="flex-1 space-y-3">
                            <div className="flex items-start justify-between">
                              <div>
                                <div className="flex items-center gap-2 mb-1">
                                  <h4 className="text-lg font-semibold">{account.display_name}</h4>
                                  <Badge variant="outline" className="capitalize">
                                    {account.platform}
                                  </Badge>
                                  {account.verified && (
                                    <Badge variant="secondary" className="text-xs">
                                      ✓ Verified
                                    </Badge>
                                  )}
                                  <Badge variant={account.is_active ? "default" : "outline"} className="text-xs">
                                    {account.is_active ? "Active" : "Inactive"}
                                  </Badge>
                                </div>
                                <p className="text-sm text-muted-foreground">@{account.username}</p>
                                <p className="text-xs text-muted-foreground">ID: {account.user_id}</p>
                              </div>
                            </div>
                            
                            {account.bio && (
                              <div className="bg-muted/50 rounded-lg p-3">
                                <p className="text-sm">{account.bio}</p>
                              </div>
                            )}
                            
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                              <div className="text-center">
                                <div className="text-lg font-semibold">{account.followers_count.toLocaleString()}</div>
                                <div className="text-xs text-muted-foreground">Followers</div>
                              </div>
                              <div className="text-center">
                                <div className="text-lg font-semibold">{account.following_count.toLocaleString()}</div>
                                <div className="text-xs text-muted-foreground">Following</div>
                              </div>
                              <div className="text-center">
                                <div className="text-sm font-medium">{account.location || 'Not set'}</div>
                                <div className="text-xs text-muted-foreground">Location</div>
                              </div>
                              <div className="text-center">
                                <div className="text-sm font-medium">{account.url ? 'Yes' : 'No'}</div>
                                <div className="text-xs text-muted-foreground">Website</div>
                              </div>
                            </div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 border-t">
                              <div>
                                <div className="text-xs text-muted-foreground mb-1">Account Created</div>
                                <div className="text-sm">{new Date(account.created_at).toLocaleDateString()}</div>
                              </div>
                              <div>
                                <div className="text-xs text-muted-foreground mb-1">Connected to Character</div>
                                <div className="text-sm">{new Date(account.connected_at).toLocaleDateString()}</div>
                              </div>
                            </div>
                            
                            {account.url && (
                              <div className="mt-2">
                                <div className="text-xs text-muted-foreground mb-1">Website</div>
                                <a href={account.url} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-600 hover:underline">
                                  {account.url}
                                </a>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-12 text-muted-foreground">
                      <Twitter className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <h3 className="text-lg font-medium mb-2">No social accounts connected</h3>
                      <p className="text-sm">This character hasn't been connected to any social media platforms yet.</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
