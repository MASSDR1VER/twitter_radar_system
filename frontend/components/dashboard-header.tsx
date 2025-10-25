"use client"

import { SidebarTrigger } from "@/components/ui/sidebar"
import { ThemeToggle } from "@/components/theme-toggle"
import { BreadcrumbNavigation, type BreadcrumbItem } from "@/components/breadcrumb-navigation"

interface DashboardHeaderProps {
  title?: string
  breadcrumbs?: BreadcrumbItem[]
  children?: React.ReactNode
  hideThemeToggle?: boolean
}

export function DashboardHeader({ title, breadcrumbs, children, hideThemeToggle = false }: DashboardHeaderProps) {
  return (
    <header className="flex items-center h-14 px-3 sm:px-4 border-b lg:h-[60px] lg:px-6">
      <div className="flex items-center gap-2 sm:gap-3 flex-1 min-w-0">
        <SidebarTrigger className="-ml-1" />
        <div className="flex flex-col gap-1">
          {breadcrumbs && breadcrumbs.length > 0 ? (
            <BreadcrumbNavigation items={breadcrumbs} />
          ) : title ? (
            <h1 className="text-lg font-semibold">{title}</h1>
          ) : null}
        </div>
      </div>
      <div className="ml-auto flex items-center gap-1 sm:gap-2">
        {children}
        {!hideThemeToggle && <ThemeToggle />}
      </div>
    </header>
  )
}