import {
  type ChartOptions,
  type Point,
  type ScriptableContext,
  Tooltip,
  type TooltipItem,
} from 'chart.js'
import { fr } from 'date-fns/locale'
import { format } from 'date-fns-tz'

import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { formatNumberLabel } from '@/commons/utils/formatNumber'

const MONTH_FORMAT = 'LLLL'
const FORMAT_OPTIONS = { locale: fr }

interface RecentViews {
  date: Date
  views: number
  rawDate: string
}

export const buildDatasets = (recentViews: RecentViews[], isV2?: boolean) => {
  return {
    datasets: [
      {
        data: recentViews.map((v) => ({
          x: v.rawDate,
          y: v.views,
        })),
        pointStyle: false as const,
        backgroundColor: (c: ScriptableContext<'bar' | 'line'>) => {
          const v = recentViews[c.dataIndex]?.views ?? 0
          if (isV2) {
            return v <= 0 ? '#f1f1f4' : 'rgba(97, 35, 223, 0.08)'
          }
          return 'rgba(97, 35, 223, 0.08)'
        },
        borderColor: (c: ScriptableContext<'bar' | 'line'>) => {
          const v = recentViews[c.dataIndex]?.views ?? 0
          if (isV2) {
            return v <= 0 ? '#CBCDD2' : 'rgba(97, 35, 223, 0)'
          }
          return 'rgba(97, 35, 223, 0)'
        },
        borderWidth: (c: ScriptableContext<'bar' | 'line'>) => {
          if (isV2 && (recentViews[c.dataIndex]?.views ?? 0) <= 0) {
            return 1
          }
          return 0
        },
        borderRadius: isV2 ? 4 : 0,
        tension: 0.4,
        fill: true,
        minBarLength: isV2 ? 4 : 0,
      },
    ],
  }
}

export const buildGraphOptions = (
  stepSize: number,
  firstMonth: string | null
): ChartOptions<'line'> => {
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
      tooltip: {
        callbacks: {
          title: (tooltipItems: TooltipItem<'line'>[]) => {
            const item = tooltipItems[0]
            if (item.parsed.x !== null) {
              const date = new Date(item.parsed.x)
              return format(date, 'd MMMM yyyy', { locale: fr })
            }
            return ''
          },
        },
      },
    },
  }
}

// @ts-expect-error
Tooltip.positioners.myCustomPositioner = (_, eventPosition: Point) => {
  return eventPosition
}

export const buildV2GraphOptions = (
  stepSize: number,
  suggestedMax: number
): ChartOptions<'bar'> => {
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
          padding: 8,
          callback: (value: string | number) => {
            const month = format(new Date(value), MONTH_FORMAT, FORMAT_OPTIONS)
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
        suggestedMax,

        grid: { display: true, drawTicks: false },
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
      tooltip: {
        // @ts-expect-error
        position: 'myCustomPositioner',
        backgroundColor: '#FFFFFF',
        borderColor: '#CBCDD2',
        borderWidth: 1,
        bodyColor: '#161617',
        titleColor: '#161617',
        padding: 16,
        cornerRadius: 8,
        titleFont: {
          size: 12,
          family: 'Montserrat-SemiBold, system-ui, sans-serif',
        },
        bodyFont: {
          size: 12,
          family: 'Montserrat-SemiBold, system-ui, sans-serif',
        },
        callbacks: {
          title: (tooltipItems: TooltipItem<'bar'>[]) => {
            const item = tooltipItems[0]
            if (item.parsed.x !== null) {
              const date = new Date(item.parsed.x)
              return `${format(date, 'LLL', { locale: fr })}`
            }
            return ''
          },
          label: (context) => {
            return `${context.parsed.y} consultations`
          },
        },
      },
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

  const lastStep = niceSteps[niceSteps.length - 1]
  assertOrFrontendError(lastStep, '`lastStep` is undefined.')
  return niceSteps.find((step) => step >= roughStep) ?? lastStep
}
