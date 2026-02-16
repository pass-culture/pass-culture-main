import { fr } from 'date-fns/locale'
import { format } from 'date-fns-tz'

import type { VenueMonthlyViewModel } from '@/apiClient/v1'

import { formatNumberLabel } from '../../../../commons/utils/formatNumber'

const MONTH_FORMAT = 'LLLL'
const FORMAT_OPTIONS = { locale: fr }

interface RecentViews {
  date: Date
  views: number
  rawMonth: number
}

interface MonthlyViewsResult {
  recentViews: RecentViews[]
  minViews: number
  maxViews: number
}

export const buildDatasets = (recentViews: RecentViews[]) => {
  return {
    datasets: [
      {
        data: recentViews.map((v) => ({
          x: v.date,
          y: v.views,
        })),
        pointStyle: false as const,
        backgroundColor: 'rgba(97, 35, 223, 0.08)',
        borderColor: 'rgba(97, 35, 223, 0)',
        borderWidth: 0,
        tension: 0.4,
        fill: true,
      },
    ],
  }
}

export const buildGraphOptions = (
  stepSize: number,
  firstMonth: string | null
) => {
  return {
    responsive: true,
    maintainAspectRatio: false,
    resizeDelay: 0,
    layout: {
      padding: {
        left: 4,
        right: 16,
        top: 8,
      },
    },
    scales: {
      x: {
        title: { display: false, text: 'Date' },
        type: 'time' as const,
        time: { unit: 'month' as const },
        adapters: { date: { locale: fr } },
        grid: { display: false, drawTicks: false },
        border: { display: false },
        ticks: {
          color: '#696A6F',
          font: {
            family: 'Montserrat-SemiBold, system-ui, sans-serif',
            size: 12,
          },
          maxRotation: 0,
          autoSkip: true,
          padding: 8,
          callback: (value: string | number) => {
            const month = format(new Date(value), MONTH_FORMAT, FORMAT_OPTIONS)
            if (firstMonth && month === firstMonth) {
              return ''
            }
            return month.charAt(0).toUpperCase() + month.slice(1)
          },
        },
      },
      y: {
        title: {
          display: true,
          text: 'Nombre total de vues',
          font: {
            family: 'Montserrat-Medium, system-ui, sans-serif',
            size: 12,
          },
          padding: { bottom: 8 },
        },
        grid: { drawTicks: false },
        ticks: {
          maxTicksLimit: 4,
          stepSize,
          color: '#696A6F',
          font: {
            family: 'Montserrat-SemiBold, system-ui, sans-serif',
            size: 12,
          },
          padding: 8,
          callback: formatNumberLabel,
        },
      },
    },
    plugins: {
      legend: { display: false },
    },
  }
}

export const computeGraphSteps = (maxViews: number, minViews: number) => {
  const range = maxViews - minViews
  if (range <= 0) {
    return 1
  }

  const roughStep = range / 3
  const magnitude = 10 ** Math.floor(Math.log10(roughStep))
  const niceSteps = [1, 2, 5, 10].map((n) => n * magnitude)

  const lastStep = niceSteps.at(-1) as number
  return niceSteps.find((step) => step >= roughStep) ?? lastStep
}

export const buildMonthlyViews = (
  monthlyViews: VenueMonthlyViewModel[]
): MonthlyViewsResult => {
  const now = new Date()
  const currentYear = now.getFullYear()
  const currentMonth = now.getMonth()
  const cutoffDate = new Date(currentYear, currentMonth - 5, 1)

  const filtered = monthlyViews
    .map((view) => {
      const year = view.month > currentMonth ? currentYear - 1 : currentYear
      const date = new Date(year, view.month - 1, 1)
      return { date, views: view.views, rawMonth: view.month }
    })
    .filter((item) => item.date >= cutoffDate)
    .sort((a, b) => a.date.getTime() - b.date.getTime())

  if (filtered.length === 0) {
    return {
      recentViews: [],
      minViews: 0,
      maxViews: 1000,
    }
  }

  const views = filtered.map((v) => v.views)
  return {
    recentViews: filtered,
    minViews: Math.min(...views),
    maxViews: Math.max(...views),
  }
}
