"use client"

import Link from "next/link"
import { ChevronRight } from "lucide-react"

export interface BreadcrumbItem {
  title: string
  href?: string
}

interface BreadcrumbNavigationProps {
  items: BreadcrumbItem[]
}

export function BreadcrumbNavigation({ items }: BreadcrumbNavigationProps) {
  if (items.length === 0) return null

  return (
    <nav className="flex items-center space-x-1 text-xs sm:text-sm text-muted-foreground">
      {items.map((item, index) => {
        const isLast = index === items.length - 1
        
        return (
          <div key={index} className="flex items-center">
            {item.href && !isLast ? (
              <Link
                href={item.href}
                className="hover:text-foreground transition-colors truncate"
              >
                <span className="hidden sm:inline">{item.title}</span>
                <span className="sm:hidden">{item.title.substring(0, 8)}{item.title.length > 8 ? '...' : ''}</span>
              </Link>
            ) : (
              <span className={isLast ? "font-medium text-foreground truncate" : "truncate"}>
                <span className="hidden sm:inline">{item.title}</span>
                <span className="sm:hidden">{item.title.substring(0, 10)}{item.title.length > 10 ? '...' : ''}</span>
              </span>
            )}
            {!isLast && (
              <ChevronRight className="mx-1 sm:mx-2 h-3 w-3 sm:h-4 sm:w-4 text-muted-foreground/50" />
            )}
          </div>
        )
      })}
    </nav>
  )
}