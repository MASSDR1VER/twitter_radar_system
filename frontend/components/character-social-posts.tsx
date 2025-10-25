"use client"

import { CalendarIcon, Heart, MessageCircle, MoreHorizontal, Repeat, Search, Twitter } from "lucide-react"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

// Mock data for social posts
const socialPosts = [
  {
    id: "post-1",
    platform: "twitter",
    content:
      "Just finished reading a fascinating paper on the ethical implications of large language models. The discussion around bias and fairness in AI systems is becoming increasingly important as these technologies become more integrated into our daily lives. #AI #Ethics #MachineLearning",
    published_at: "2023-06-15T10:30:00Z",
    status: "published",
    metrics: {
      likes: 45,
      shares: 12,
      comments: 8,
      views: 1200,
    },
  },
  {
    id: "post-2",
    platform: "twitter",
    content:
      "Excited to be attending the AI Ethics Conference next month! Looking forward to discussions on responsible AI development and deployment. Who else is going? #AIEthics #Conference",
    published_at: "2023-06-10T14:15:00Z",
    status: "published",
    metrics: {
      likes: 32,
      shares: 8,
      comments: 5,
      views: 950,
    },
  },
  {
    id: "post-3",
    platform: "twitter",
    content:
      "Today's hike in the mountains was exactly what I needed to clear my mind. Nature has a way of providing perspective on complex problems. #Hiking #Nature #MentalClarity",
    published_at: "2023-06-05T18:45:00Z",
    status: "published",
    metrics: {
      likes: 67,
      shares: 15,
      comments: 12,
      views: 1500,
    },
  },
  {
    id: "post-4",
    platform: "twitter",
    content:
      "Working on a new research project exploring the intersection of machine learning and cognitive science. The way humans learn and process information can teach us a lot about improving AI systems. #Research #MachineLearning #CognitiveScience",
    published_at: null,
    status: "scheduled",
    scheduled_for: "2023-06-20T09:00:00Z",
    metrics: {
      likes: 0,
      shares: 0,
      comments: 0,
      views: 0,
    },
  },
]

interface CharacterSocialPostsProps {
  characterId: string
}

export function CharacterSocialPosts({ characterId }: CharacterSocialPostsProps) {
  return (
    <div className="space-y-4">
      <Tabs defaultValue="published">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
          <TabsList>
            <TabsTrigger value="published">Published</TabsTrigger>
            <TabsTrigger value="scheduled">Scheduled</TabsTrigger>
            <TabsTrigger value="drafts">Drafts</TabsTrigger>
          </TabsList>
          <div className="relative flex-1 sm:max-w-[300px]">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input placeholder="Search posts..." className="pl-8" />
          </div>
          <Button variant="outline" size="sm" className="h-9 gap-1 sm:w-auto">
            <CalendarIcon className="h-4 w-4" />
            <span>Filter by Date</span>
          </Button>
        </div>

        <TabsContent value="published" className="mt-4">
          <div className="grid gap-4">
            {socialPosts
              .filter((post) => post.status === "published")
              .map((post) => (
                <Card key={post.id}>
                  <CardHeader className="flex flex-row items-start gap-4 space-y-0 pb-2">
                    <Avatar className="h-10 w-10">
                      <AvatarImage src={`https://api.dicebear.com/7.x/personas/svg?seed=Alex`} alt="Alex" />
                      <AvatarFallback>AT</AvatarFallback>
                    </Avatar>
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold">Alex Tech</span>
                        <span className="text-sm text-muted-foreground">@alextech</span>
                        <Badge variant="outline" className="flex items-center gap-1">
                          <Twitter className="h-3 w-3" />
                          <span>Twitter</span>
                        </Badge>
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {new Date(post.published_at!).toLocaleString()}
                      </div>
                    </div>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                          <MoreHorizontal className="h-4 w-4" />
                          <span className="sr-only">More options</span>
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem>View Analytics</DropdownMenuItem>
                        <DropdownMenuItem>Copy Link</DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem className="text-destructive">Delete Post</DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm">{post.content}</p>
                  </CardContent>
                  <CardFooter className="border-t pt-4">
                    <div className="flex w-full justify-between text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Heart className="h-4 w-4" />
                        <span>{post.metrics.likes}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Repeat className="h-4 w-4" />
                        <span>{post.metrics.shares}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <MessageCircle className="h-4 w-4" />
                        <span>{post.metrics.comments}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <span>{post.metrics.views} views</span>
                      </div>
                    </div>
                  </CardFooter>
                </Card>
              ))}
          </div>
        </TabsContent>

        <TabsContent value="scheduled" className="mt-4">
          <div className="grid gap-4">
            {socialPosts
              .filter((post) => post.status === "scheduled")
              .map((post) => (
                <Card key={post.id}>
                  <CardHeader className="flex flex-row items-start gap-4 space-y-0 pb-2">
                    <Avatar className="h-10 w-10">
                      <AvatarImage src={`https://api.dicebear.com/7.x/personas/svg?seed=Alex`} alt="Alex" />
                      <AvatarFallback>AT</AvatarFallback>
                    </Avatar>
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold">Alex Tech</span>
                        <span className="text-sm text-muted-foreground">@alextech</span>
                        <Badge variant="outline" className="flex items-center gap-1">
                          <Twitter className="h-3 w-3" />
                          <span>Twitter</span>
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="secondary">Scheduled</Badge>
                        <span className="text-xs text-muted-foreground">
                          {new Date(post.scheduled_for!).toLocaleString()}
                        </span>
                      </div>
                    </div>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                          <MoreHorizontal className="h-4 w-4" />
                          <span className="sr-only">More options</span>
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem>Edit Post</DropdownMenuItem>
                        <DropdownMenuItem>Reschedule</DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem className="text-destructive">Cancel Post</DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm">{post.content}</p>
                  </CardContent>
                </Card>
              ))}
            {socialPosts.filter((post) => post.status === "scheduled").length === 0 && (
              <div className="rounded-lg border border-dashed p-8 text-center">
                <h3 className="text-lg font-medium">No Scheduled Posts</h3>
                <p className="mt-2 text-sm text-muted-foreground">
                  You don't have any posts scheduled for publication.
                </p>
                <Button className="mt-4">Schedule a Post</Button>
              </div>
            )}
          </div>
        </TabsContent>

        <TabsContent value="drafts" className="mt-4">
          <div className="rounded-lg border border-dashed p-8 text-center">
            <h3 className="text-lg font-medium">No Draft Posts</h3>
            <p className="mt-2 text-sm text-muted-foreground">You don't have any draft posts saved.</p>
            <Button className="mt-4">Create a Draft</Button>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
