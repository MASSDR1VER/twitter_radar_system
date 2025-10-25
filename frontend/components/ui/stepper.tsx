"use client"

import React from "react"
import { Check, ChevronRight } from "lucide-react"
import { cn } from "@/lib/utils"

interface Step {
  id: string
  title: string
  description?: string
  isCompleted?: boolean
  isActive?: boolean
}

interface StepperProps {
  steps: Step[]
  currentStep: number
  className?: string
}

export function Stepper({ steps, currentStep, className }: StepperProps) {
  return (
    <div className={cn("w-full", className)}>
      <nav aria-label="Progress">
        <ol className="flex items-center justify-center gap-4">
          {steps.map((step, index) => {
            const isCompleted = index < currentStep
            const isActive = index === currentStep
            const isLast = index === steps.length - 1

            return (
              <li key={step.id} className="flex items-center gap-4">
                <div className="flex flex-col items-center gap-2">
                  <div
                    className={cn(
                      "flex h-8 w-8 items-center justify-center rounded-full transition-all duration-200",
                      isCompleted && "bg-primary text-primary-foreground",
                      isActive && "bg-primary text-primary-foreground",
                      !isCompleted && !isActive && "bg-muted text-muted-foreground"
                    )}
                  >
                    {isCompleted ? (
                      <Check className="h-4 w-4" />
                    ) : (
                      <span className="text-xs font-medium">{index + 1}</span>
                    )}
                  </div>
                  <div className="text-xs font-medium text-center min-w-16">
                    <div
                      className={cn(
                        "transition-colors",
                        (isActive || isCompleted) && "text-foreground",
                        !isCompleted && !isActive && "text-muted-foreground"
                      )}
                    >
                      {step.title}
                    </div>
                  </div>
                </div>
                {!isLast && (
                  <div className="w-8 h-px bg-muted" />
                )}
              </li>
            )
          })}
        </ol>
      </nav>
    </div>
  )
}

interface StepContainerProps {
  children: React.ReactNode
  title: string
  description?: string
  className?: string
}

export function StepContainer({ children, title, description, className }: StepContainerProps) {
  return (
    <div className={cn("space-y-6", className)}>
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-semibold">{title}</h2>
        {description && (
          <p className="text-muted-foreground">{description}</p>
        )}
      </div>
      {children}
    </div>
  )
}

interface StepNavigationProps {
  currentStep: number
  totalSteps: number
  onNext?: () => void
  onPrevious?: () => void
  onSkip?: () => void
  nextLabel?: string
  previousLabel?: string
  skipLabel?: string
  isNextDisabled?: boolean
  isNextLoading?: boolean
  showSkip?: boolean
  className?: string
}

export function StepNavigation({
  currentStep,
  totalSteps,
  onNext,
  onPrevious,
  onSkip,
  nextLabel = "Next",
  previousLabel = "Previous", 
  skipLabel = "Skip",
  isNextDisabled = false,
  isNextLoading = false,
  showSkip = false,
  className
}: StepNavigationProps) {
  const isFirstStep = currentStep === 0
  const isLastStep = currentStep === totalSteps - 1

  return (
    <div className={cn("flex justify-between items-center pt-6 mt-6", className)}>
      <div>
        {!isFirstStep && onPrevious ? (
          <button
            onClick={onPrevious}
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            <ChevronRight className="h-4 w-4 rotate-180 mr-1" />
            {previousLabel}
          </button>
        ) : (
          <div />
        )}
      </div>

      <div className="flex items-center gap-3">
        {showSkip && onSkip && !isLastStep && (
          <button
            onClick={onSkip}
            className="px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            {skipLabel}
          </button>
        )}
        
        {onNext && (
          <button
            onClick={onNext}
            disabled={isNextDisabled || isNextLoading}
            className={cn(
              "inline-flex items-center px-6 py-2.5 text-sm font-medium rounded-md transition-colors",
              "bg-primary text-primary-foreground hover:bg-primary/90",
              "disabled:opacity-50 disabled:cursor-not-allowed"
            )}
          >
            {isNextLoading ? "Loading..." : isLastStep ? "Complete" : nextLabel}
            {!isLastStep && !isNextLoading && <ChevronRight className="h-4 w-4 ml-1" />}
          </button>
        )}
      </div>
    </div>
  )
}