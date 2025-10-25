"use client"

import { useState } from "react"
import { Search, Tag, Trash2 } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

// Mock data for knowledge items
const knowledgeItems = [
  {
    memory_id: "mem-1",
    content: "The character is an AI researcher focused on ethical AI development.",
    importance: 9,
    tags: ["background", "profession"],
    created_at: "2023-05-15T12:00:00Z",
    source: "user_provided",
    manually_added: true,
  },
  {
    memory_id: "mem-2",
    content: "The character enjoys hiking in the mountains during weekends.",
    importance: 6,
    tags: ["hobby", "personal"],
    created_at: "2023-05-16T14:30:00Z",
    source: "conversation",
    manually_added: false,
  },
  {
    memory_id: "mem-3",
    content: "The character believes that AI systems should be transparent and explainable.",
    importance: 8,
    tags: ["belief", "ethics"],
    created_at: "2023-05-17T09:15:00Z",
    source: "user_provided",
    manually_added: true,
  },
  {
    memory_id: "mem-4",
    content: "The character has a Ph.D. in Computer Science with a focus on machine learning.",
    importance: 7,
    tags: ["education", "background"],
    created_at: "2023-05-18T11:45:00Z",
    source: "user_provided",
    manually_added: true,
  },
  {
    memory_id: "mem-5",
    content: "The character prefers tea over coffee in the morning.",
    importance: 3,
    tags: ["preference", "personal"],
    created_at: "2023-05-19T08:20:00Z",
    source: "conversation",
    manually_added: false,
  },
]

interface CharacterKnowledgeListProps {
  characterId: string
}

export function CharacterKnowledgeList({ characterId }: CharacterKnowledgeListProps) {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedTags, setSelectedTags] = useState<string[]>([])

  // Get all unique tags
  const allTags = Array.from(new Set(knowledgeItems.flatMap((item) => item.tags))).sort()

  // Filter knowledge items based on search query and selected tags
  const filteredItems = knowledgeItems.filter((item) => {
    const matchesSearch = item.content.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesTags = selectedTags.length === 0 || selectedTags.some((tag) => item.tags.includes(tag))
    return matchesSearch && matchesTags
  })

  // Toggle tag selection
  const toggleTag = (tag: string) => {
    setSelectedTags((prev) => (prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]))
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-4 md:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search knowledge..."
            className="pl-8"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" size="sm" className="h-9 gap-1">
            <Tag className="h-4 w-4" />
            <span>Filter by Tags</span>
          </Button>
          {allTags.map((tag) => (
            <Badge
              key={tag}
              variant={selectedTags.includes(tag) ? "default" : "outline"}
              className="cursor-pointer"
              onClick={() => toggleTag(tag)}
            >
              {tag}
            </Badge>
          ))}
        </div>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[50%]">Content</TableHead>
              <TableHead>Importance</TableHead>
              <TableHead>Tags</TableHead>
              <TableHead>Source</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredItems.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="h-24 text-center">
                  No knowledge items found.
                </TableCell>
              </TableRow>
            ) : (
              filteredItems.map((item) => (
                <TableRow key={item.memory_id}>
                  <TableCell className="font-medium">{item.content}</TableCell>
                  <TableCell>
                    <Badge variant={item.importance > 7 ? "default" : "outline"}>{item.importance}/10</Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-1">
                      {item.tags.map((tag) => (
                        <Badge key={tag} variant="secondary" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{item.source === "user_provided" ? "Manual" : "Learned"}</Badge>
                  </TableCell>
                  <TableCell>{new Date(item.created_at).toLocaleDateString()}</TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                      <Trash2 className="h-4 w-4" />
                      <span className="sr-only">Delete</span>
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
