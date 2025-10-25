"use client"

import { useState } from "react"
import {
  Check,
  Edit,
  Filter,
  Key,
  Lock,
  MoreHorizontal,
  Plus,
  Search,
  Shield,
  Trash2,
  Unlock,
  User,
  UserPlus,
  Clock,
} from "lucide-react"
import Link from "next/link"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { DashboardHeader } from "@/components/dashboard-header"

// Mock data for users
const users = [
  {
    id: "user-1",
    name: "John Smith",
    email: "john.smith@example.com",
    avatar: "https://api.dicebear.com/7.x/personas/svg?seed=John Smith",
    role: "admin",
    status: "active",
    lastActive: "2023-06-15T10:30:00Z",
    createdAt: "2023-01-10T08:00:00Z",
  },
  {
    id: "user-2",
    name: "Sarah Johnson",
    email: "sarah.johnson@example.com",
    avatar: "https://api.dicebear.com/7.x/personas/svg?seed=Sarah Johnson",
    role: "editor",
    status: "active",
    lastActive: "2023-06-14T15:45:00Z",
    createdAt: "2023-02-15T09:30:00Z",
  },
  {
    id: "user-3",
    name: "Michael Brown",
    email: "michael.brown@example.com",
    avatar: "https://api.dicebear.com/7.x/personas/svg?seed=Michael Brown",
    role: "viewer",
    status: "active",
    lastActive: "2023-06-13T11:20:00Z",
    createdAt: "2023-03-05T14:15:00Z",
  },
  {
    id: "user-4",
    name: "Emily Davis",
    email: "emily.davis@example.com",
    avatar: "https://api.dicebear.com/7.x/personas/svg?seed=Emily Davis",
    role: "editor",
    status: "inactive",
    lastActive: "2023-05-20T09:10:00Z",
    createdAt: "2023-03-10T11:45:00Z",
  },
  {
    id: "user-5",
    name: "David Wilson",
    email: "david.wilson@example.com",
    avatar: "https://api.dicebear.com/7.x/personas/svg?seed=David Wilson",
    role: "viewer",
    status: "pending",
    lastActive: null,
    createdAt: "2023-06-10T16:30:00Z",
  },
]

// Mock data for roles
const roles = [
  {
    id: "role-1",
    name: "Admin",
    description: "Full access to all features and settings",
    users: 1,
    permissions: [
      "Manage users",
      "Manage characters",
      "Manage system settings",
      "View analytics",
      "Export data",
      "Delete data",
    ],
  },
  {
    id: "role-2",
    name: "Editor",
    description: "Can create and edit characters and content",
    users: 2,
    permissions: ["Create characters", "Edit characters", "View analytics", "Export data"],
  },
  {
    id: "role-3",
    name: "Viewer",
    description: "Read-only access to characters and content",
    users: 2,
    permissions: ["View characters", "View analytics"],
  },
]

export default function UserManagementPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedRole, setSelectedRole] = useState<string>("all")
  const [selectedStatus, setSelectedStatus] = useState<string>("all")
  const [activeTab, setActiveTab] = useState("users")
  const [isAddUserDialogOpen, setIsAddUserDialogOpen] = useState(false)
  const [isAddRoleDialogOpen, setIsAddRoleDialogOpen] = useState(false)

  // Filter users based on search query and filters
  const filteredUsers = users.filter(
    (user) =>
      (user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        user.email.toLowerCase().includes(searchQuery.toLowerCase())) &&
      (selectedRole === "all" || user.role === selectedRole) &&
      (selectedStatus === "all" || user.status === selectedStatus),
  )

  return (
    <div className="flex flex-col w-full">
      <DashboardHeader 
        breadcrumbs={[
          { title: "System", href: "/system" },
          { title: "User Management" }
        ]}
      >
        <Dialog open={isAddUserDialogOpen} onOpenChange={setIsAddUserDialogOpen}>
          <DialogTrigger asChild>
            <Button size="sm" className="h-8 gap-1">
              <UserPlus className="h-4 w-4" />
              <span>Add User</span>
            </Button>
          </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle>Add New User</DialogTitle>
                <DialogDescription>Create a new user account and assign permissions.</DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="name">Full Name</Label>
                  <Input id="name" placeholder="Enter user's full name" />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" type="email" placeholder="Enter user's email address" />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="role">Role</Label>
                  <Select>
                    <SelectTrigger id="role">
                      <SelectValue placeholder="Select role" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="admin">Admin</SelectItem>
                      <SelectItem value="editor">Editor</SelectItem>
                      <SelectItem value="viewer">Viewer</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="password">Temporary Password</Label>
                  <Input id="password" type="password" placeholder="Enter temporary password" />
                  <p className="text-xs text-muted-foreground">
                    User will be prompted to change this password on first login.
                  </p>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsAddUserDialogOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" onClick={() => setIsAddUserDialogOpen(false)}>
                  Add User
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
      </DashboardHeader>

      <div className="flex-1 p-4 md:p-6">
        <div className="mx-auto max-w-6xl space-y-6">

          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <div className="flex flex-col gap-4 md:flex-row md:items-center">
              <TabsList>
                <TabsTrigger value="users">Users</TabsTrigger>
                <TabsTrigger value="roles">Roles & Permissions</TabsTrigger>
              </TabsList>
              {activeTab === "users" && (
                <div className="flex flex-1 flex-col gap-2 md:flex-row">
                  <div className="relative flex-1">
                    <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search users..."
                      className="pl-8"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                    />
                  </div>
                  <div className="flex gap-2">
                    <Select value={selectedRole} onValueChange={setSelectedRole}>
                      <SelectTrigger className="w-full md:w-[150px]">
                        <SelectValue placeholder="All Roles" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Roles</SelectItem>
                        <SelectItem value="admin">Admin</SelectItem>
                        <SelectItem value="editor">Editor</SelectItem>
                        <SelectItem value="viewer">Viewer</SelectItem>
                      </SelectContent>
                    </Select>
                    <Select value={selectedStatus} onValueChange={setSelectedStatus}>
                      <SelectTrigger className="w-full md:w-[150px]">
                        <SelectValue placeholder="All Status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Status</SelectItem>
                        <SelectItem value="active">Active</SelectItem>
                        <SelectItem value="inactive">Inactive</SelectItem>
                        <SelectItem value="pending">Pending</SelectItem>
                      </SelectContent>
                    </Select>
                    <Button variant="outline" size="sm" className="h-9 gap-1">
                      <Filter className="h-4 w-4" />
                      <span>Filter</span>
                    </Button>
                  </div>
                </div>
              )}
              {activeTab === "roles" && (
                <div className="flex flex-1 justify-end">
                  <Dialog open={isAddRoleDialogOpen} onOpenChange={setIsAddRoleDialogOpen}>
                    <DialogTrigger asChild>
                      <Button size="sm" className="h-9 gap-1">
                        <Plus className="h-4 w-4" />
                        <span>Create Role</span>
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="sm:max-w-[500px]">
                      <DialogHeader>
                        <DialogTitle>Create New Role</DialogTitle>
                        <DialogDescription>Define a new role with custom permissions.</DialogDescription>
                      </DialogHeader>
                      <div className="grid gap-4 py-4">
                        <div className="grid gap-2">
                          <Label htmlFor="role-name">Role Name</Label>
                          <Input id="role-name" placeholder="Enter role name" />
                        </div>
                        <div className="grid gap-2">
                          <Label htmlFor="role-description">Description</Label>
                          <Input id="role-description" placeholder="Enter role description" />
                        </div>
                        <div className="grid gap-2">
                          <Label>Permissions</Label>
                          <div className="space-y-2 rounded-md border p-4">
                            <div className="flex items-center space-x-2">
                              <input type="checkbox" id="perm-view-characters" className="h-4 w-4" defaultChecked />
                              <Label htmlFor="perm-view-characters" className="font-normal">
                                View Characters
                              </Label>
                            </div>
                            <div className="flex items-center space-x-2">
                              <input type="checkbox" id="perm-create-characters" className="h-4 w-4" defaultChecked />
                              <Label htmlFor="perm-create-characters" className="font-normal">
                                Create Characters
                              </Label>
                            </div>
                            <div className="flex items-center space-x-2">
                              <input type="checkbox" id="perm-edit-characters" className="h-4 w-4" defaultChecked />
                              <Label htmlFor="perm-edit-characters" className="font-normal">
                                Edit Characters
                              </Label>
                            </div>
                            <div className="flex items-center space-x-2">
                              <input type="checkbox" id="perm-delete-characters" className="h-4 w-4" />
                              <Label htmlFor="perm-delete-characters" className="font-normal">
                                Delete Characters
                              </Label>
                            </div>
                            <div className="flex items-center space-x-2">
                              <input type="checkbox" id="perm-view-analytics" className="h-4 w-4" defaultChecked />
                              <Label htmlFor="perm-view-analytics" className="font-normal">
                                View Analytics
                              </Label>
                            </div>
                            <div className="flex items-center space-x-2">
                              <input type="checkbox" id="perm-manage-users" className="h-4 w-4" />
                              <Label htmlFor="perm-manage-users" className="font-normal">
                                Manage Users
                              </Label>
                            </div>
                            <div className="flex items-center space-x-2">
                              <input type="checkbox" id="perm-system-settings" className="h-4 w-4" />
                              <Label htmlFor="perm-system-settings" className="font-normal">
                                System Settings
                              </Label>
                            </div>
                          </div>
                        </div>
                      </div>
                      <DialogFooter>
                        <Button variant="outline" onClick={() => setIsAddRoleDialogOpen(false)}>
                          Cancel
                        </Button>
                        <Button type="submit" onClick={() => setIsAddRoleDialogOpen(false)}>
                          Create Role
                        </Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>
                </div>
              )}
            </div>

            <TabsContent value="users" className="mt-6">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle>User Accounts</CardTitle>
                  <CardDescription>
                    {filteredUsers.length} user {filteredUsers.length === 1 ? "account" : "accounts"} found
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="rounded-md border overflow-x-auto">
                    <Table className="min-w-[600px]">
                      <TableHeader>
                        <TableRow>
                          <TableHead>User</TableHead>
                          <TableHead>Role</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead className="hidden md:table-cell">Last Active</TableHead>
                          <TableHead className="hidden lg:table-cell">Created</TableHead>
                          <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {filteredUsers.length === 0 ? (
                          <TableRow>
                            <TableCell colSpan={6} className="h-24 text-center">
                              No users found.
                            </TableCell>
                          </TableRow>
                        ) : (
                          filteredUsers.map((user) => (
                            <TableRow key={user.id}>
                              <TableCell>
                                <div className="flex items-center gap-3">
                                  <Avatar className="h-9 w-9">
                                    <AvatarImage src={user.avatar || "/placeholder.svg"} alt={user.name} />
                                    <AvatarFallback>{user.name.substring(0, 2).toUpperCase()}</AvatarFallback>
                                  </Avatar>
                                  <div>
                                    <div className="font-medium">{user.name}</div>
                                    <div className="text-sm text-muted-foreground">{user.email}</div>
                                  </div>
                                </div>
                              </TableCell>
                              <TableCell>
                                <Badge
                                  variant="outline"
                                  className={
                                    user.role === "admin"
                                      ? "border-blue-500 text-blue-500"
                                      : user.role === "editor"
                                        ? "border-green-500 text-green-500"
                                        : "border-amber-500 text-amber-500"
                                  }
                                >
                                  <div className="flex items-center gap-1">
                                    {user.role === "admin" ? (
                                      <Shield className="h-3 w-3" />
                                    ) : user.role === "editor" ? (
                                      <Edit className="h-3 w-3" />
                                    ) : (
                                      <User className="h-3 w-3" />
                                    )}
                                    <span className="capitalize">{user.role}</span>
                                  </div>
                                </Badge>
                              </TableCell>
                              <TableCell>
                                <Badge
                                  variant={
                                    user.status === "active"
                                      ? "default"
                                      : user.status === "pending"
                                        ? "outline"
                                        : "secondary"
                                  }
                                  className={user.status === "inactive" ? "bg-muted text-muted-foreground" : undefined}
                                >
                                  <div className="flex items-center gap-1">
                                    {user.status === "active" ? (
                                      <Check className="h-3 w-3" />
                                    ) : user.status === "pending" ? (
                                      <Clock className="h-3 w-3" />
                                    ) : (
                                      <Lock className="h-3 w-3" />
                                    )}
                                    <span className="capitalize">{user.status}</span>
                                  </div>
                                </Badge>
                              </TableCell>
                              <TableCell className="hidden md:table-cell">
                                {user.lastActive ? new Date(user.lastActive).toLocaleDateString() : "Never"}
                              </TableCell>
                              <TableCell className="hidden lg:table-cell">{new Date(user.createdAt).toLocaleDateString()}</TableCell>
                              <TableCell className="text-right">
                                <div className="flex justify-end gap-2">
                                  <Button variant="outline" size="sm" className="h-8">
                                    <Edit className="sm:mr-2 h-4 w-4" />
                                    <span className="hidden sm:inline">Edit</span>
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
                                        <User className="mr-2 h-4 w-4" />
                                        <span>View Profile</span>
                                      </DropdownMenuItem>
                                      <DropdownMenuItem>
                                        <Key className="mr-2 h-4 w-4" />
                                        <span>Reset Password</span>
                                      </DropdownMenuItem>
                                      {user.status === "active" ? (
                                        <DropdownMenuItem>
                                          <Lock className="mr-2 h-4 w-4" />
                                          <span>Deactivate Account</span>
                                        </DropdownMenuItem>
                                      ) : (
                                        <DropdownMenuItem>
                                          <Unlock className="mr-2 h-4 w-4" />
                                          <span>Activate Account</span>
                                        </DropdownMenuItem>
                                      )}
                                      <DropdownMenuSeparator />
                                      <DropdownMenuItem className="text-destructive">
                                        <Trash2 className="mr-2 h-4 w-4" />
                                        <span>Delete Account</span>
                                      </DropdownMenuItem>
                                    </DropdownMenuContent>
                                  </DropdownMenu>
                                </div>
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

            <TabsContent value="roles" className="mt-6">
              <div className="grid gap-6 md:grid-cols-2">
                {roles.map((role) => (
                  <Card key={role.id}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-xl">{role.name}</CardTitle>
                        <Badge variant="outline">{role.users} Users</Badge>
                      </div>
                      <CardDescription>{role.description}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <h4 className="text-sm font-medium">Permissions</h4>
                        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                          {role.permissions.map((permission, index) => (
                            <div key={index} className="flex items-center gap-2">
                              <Check className="h-4 w-4 text-green-500" />
                              <span className="text-sm">{permission}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </CardContent>
                    <CardFooter className="flex justify-between">
                      <Button variant="outline" size="sm">
                        <User className="mr-2 h-4 w-4" />
                        View Users
                      </Button>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm">
                          <Edit className="mr-2 h-4 w-4" />
                          Edit
                        </Button>
                        {role.name !== "Admin" && (
                          <Button variant="outline" size="sm" className="text-destructive">
                            <Trash2 className="mr-2 h-4 w-4" />
                            Delete
                          </Button>
                        )}
                      </div>
                    </CardFooter>
                  </Card>
                ))}
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  )
}
