"use client"

import { CalendarIcon, MessageSquare, Search } from "lucide-react"
import Link from "next/link"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

// Mock data for conversations
const conversations = [
  {
    id: "conv-1",
    started_at: "2023-06-15T12:00:00Z",
    updated_at: "2023-06-15T14:00:00Z",
    is_active: true,
    message_count: 24,
    last_message: "I'll look into that research paper and get back to you.",
  },
  {
    id: "conv-2",
    started_at: "2023-06-10T09:30:00Z",
    updated_at: "2023-06-10T11:45:00Z",
    is_active: false,
    message_count: 18,
    last_message: "Thanks for the interesting discussion about AI ethics.",
  },
  {
    id: "conv-3",
    started_at: "2023-06-05T15:20:00Z",
    updated_at: "2023-06-05T16:30:00Z",
    is_active: false,
    message_count: 12,
    last_message: "Let's continue this conversation later.",
  },
  {
    id: "conv-4",
    started_at: "2023-05-28T10:15:00Z",
    updated_at: "2023-05-28T11:30:00Z",
    is_active: false,
    message_count: 30,
    last_message: "I've shared some resources about machine learning algorithms.",
  },
  {
    id: "conv-5",
    started_at: "2023-05-20T14:00:00Z",
    updated_at: "2023-05-20T15:45:00Z",
    is_active: false,
    message_count: 15,
    last_message: "That's an interesting perspective on the future of AI.",
  },
]

interface CharacterConversationListProps {
  characterId: string
}

export function CharacterConversationList({ characterId }: CharacterConversationListProps) {
  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-4 sm:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input placeholder="Search conversations..." className="pl-8" />
        </div>
        <Button variant="outline" size="sm" className="h-9 gap-1 sm:w-auto">
          <CalendarIcon className="h-4 w-4" />
          <span>Filter by Date</span>
        </Button>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Status</TableHead>
              <TableHead>Last Message</TableHead>
              <TableHead>Messages</TableHead>
              <TableHead>Started</TableHead>
              <TableHead>Last Updated</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {conversations.map((conversation) => (
              <TableRow key={conversation.id}>
                <TableCell>
                  <Badge variant={conversation.is_active ? "default" : "outline"}>
                    {conversation.is_active ? "Active" : "Closed"}
                  </Badge>
                </TableCell>
                <TableCell className="font-medium max-w-[300px] truncate">{conversation.last_message}</TableCell>
                <TableCell>{conversation.message_count}</TableCell>
                <TableCell>{new Date(conversation.started_at).toLocaleDateString()}</TableCell>
                <TableCell>{new Date(conversation.updated_at).toLocaleDateString()}</TableCell>
                <TableCell className="text-right">
                  <Button asChild size="sm" variant="outline" className="h-8">
                    <Link href={`/characters/${characterId}/conversations/${conversation.id}`}>
                      <MessageSquare className="mr-2 h-4 w-4" />
                      View
                    </Link>
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
