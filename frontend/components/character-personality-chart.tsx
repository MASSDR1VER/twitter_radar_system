"use client"

import { useEffect, useRef } from "react"
import { useTheme } from "next-themes"
import { Chart, RadarController, RadialLinearScale, PointElement, LineElement, Tooltip, Legend } from "chart.js"

Chart.register(RadarController, RadialLinearScale, PointElement, LineElement, Tooltip, Legend)

interface PersonalityChartProps {
  personality: {
    curiosity: number
    empathy: number
    humor: number
    wit: number
    openness: number
    conscientiousness: number
    extraversion: number
    agreeableness: number
    neuroticism: number
  }
}

export function CharacterPersonalityChart({ personality }: PersonalityChartProps) {
  const chartRef = useRef<HTMLCanvasElement>(null)
  const chartInstance = useRef<Chart | null>(null)
  const { theme, resolvedTheme } = useTheme()

  useEffect(() => {
    if (!chartRef.current) return

    // Destroy existing chart
    if (chartInstance.current) {
      chartInstance.current.destroy()
    }

    const ctx = chartRef.current.getContext("2d")
    if (!ctx) return

    const labels = Object.keys(personality).map((key) => key.charAt(0).toUpperCase() + key.slice(1))
    const data = Object.values(personality)

    // Theme-aware colors
    const isDark = resolvedTheme === 'dark'
    const textColor = isDark ? '#e5e7eb' : '#374151'
    const gridColor = isDark ? '#374151' : '#e5e7eb'
    const pointBorderColor = isDark ? '#1f2937' : '#fff'

    chartInstance.current = new Chart(ctx, {
      type: "radar",
      data: {
        labels,
        datasets: [
          {
            label: "Personality Traits",
            data,
            backgroundColor: "rgba(147, 51, 234, 0.2)",
            borderColor: "rgba(147, 51, 234, 1)",
            borderWidth: 2,
            pointBackgroundColor: "rgba(147, 51, 234, 1)",
            pointBorderColor: pointBorderColor,
            pointHoverBackgroundColor: pointBorderColor,
            pointHoverBorderColor: "rgba(147, 51, 234, 1)",
          },
        ],
      },
      options: {
        scales: {
          r: {
            angleLines: {
              display: true,
              color: gridColor,
            },
            grid: {
              color: gridColor,
            },
            pointLabels: {
              color: textColor,
              font: {
                size: 12,
              },
            },
            ticks: {
              display: false,
            },
            suggestedMin: 0,
            suggestedMax: 10,
          },
        },
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            backgroundColor: isDark ? '#1f2937' : '#fff',
            titleColor: textColor,
            bodyColor: textColor,
            borderColor: gridColor,
            borderWidth: 1,
          },
        },
      },
    })

    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy()
      }
    }
  }, [personality, resolvedTheme])

  return <canvas ref={chartRef} />
}
