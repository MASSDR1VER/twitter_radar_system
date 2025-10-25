"use client"

import { useEffect, useRef } from "react"
import { Chart, LineController, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend } from "chart.js"

Chart.register(LineController, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend)

interface ActivityOverview {
  month?: string
  date?: string
  chat_messages: number
  social_posts: number
}

interface CharacterActivityChartProps {
  data?: ActivityOverview[]
}

export function CharacterActivityChart({ data }: CharacterActivityChartProps) {
  const chartRef = useRef<HTMLCanvasElement>(null)
  const chartInstance = useRef<Chart | null>(null)

  useEffect(() => {
    if (!chartRef.current) return

    // Destroy existing chart
    if (chartInstance.current) {
      chartInstance.current.destroy()
    }

    const ctx = chartRef.current.getContext("2d")
    if (!ctx) return

    // Prepare chart data from props or use fallback
    const chartData = data && data.length > 0 ? {
      labels: data.map(item => {
        if (item.month) return item.month
        if (item.date) {
          const date = new Date(item.date)
          return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
        }
        return 'Unknown'
      }),
      datasets: [
        {
          label: "Chat Messages",
          data: data.map(item => item.chat_messages),
          borderColor: "rgba(75, 192, 192, 1)",
          backgroundColor: "rgba(75, 192, 192, 0.2)",
          tension: 0.4,
        },
        {
          label: "Social Posts",
          data: data.map(item => item.social_posts),
          borderColor: "rgba(153, 102, 255, 1)",
          backgroundColor: "rgba(153, 102, 255, 0.2)",
          tension: 0.4,
        },
      ],
    } : {
      labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"],
      datasets: [
        {
          label: "Chat Messages",
          data: [0, 0, 0, 0, 0, 0, 0],
          borderColor: "rgba(75, 192, 192, 1)",
          backgroundColor: "rgba(75, 192, 192, 0.2)",
          tension: 0.4,
        },
        {
          label: "Social Posts",
          data: [0, 0, 0, 0, 0, 0, 0],
          borderColor: "rgba(153, 102, 255, 1)",
          backgroundColor: "rgba(153, 102, 255, 0.2)",
          tension: 0.4,
        },
      ],
    }

    chartInstance.current = new Chart(ctx, {
      type: "line",
      data: chartData,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "top",
            labels: {
              boxWidth: 12,
              padding: 15,
              font: {
                size: 12
              }
            }
          },
          tooltip: {
            mode: "index",
            intersect: false,
          },
        },
        scales: {
          x: {
            grid: {
              display: false
            },
            ticks: {
              font: {
                size: 11
              }
            }
          },
          y: {
            beginAtZero: true,
            grid: {
              color: 'rgba(0,0,0,0.1)'
            },
            ticks: {
              font: {
                size: 11
              }
            }
          },
        },
        interaction: {
          mode: "nearest",
          axis: "x",
          intersect: false,
        },
        elements: {
          point: {
            radius: 3,
            hoverRadius: 6
          },
          line: {
            borderWidth: 2
          }
        }
      },
    })

    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy()
      }
    }
  }, [data])

  return <canvas ref={chartRef} className="w-full h-full" />
}
