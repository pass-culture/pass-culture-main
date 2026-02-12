import type { Chart as ChartJS } from 'chart.js'
import {
  Chart,
  Filler,
  LinearScale,
  LineController,
  LineElement,
  PointElement,
  TimeSeriesScale,
  Tooltip,
} from 'chart.js'
import { startOfMonth, subMonths } from 'date-fns'
import { fr } from 'date-fns/locale'
import { format } from 'date-fns-tz'
import { useId, useMemo, useRef } from 'react'
import { Line } from 'react-chartjs-2'
import 'chartjs-adapter-date-fns'

import type { OffererViewsModel } from '@/apiClient/v1'
import { getDateTimeToFrenchText } from '@/commons/utils/date'
import { formatNumberLabel } from '@/commons/utils/formatNumber'
import { pluralizeFr } from '@/commons/utils/pluralize'

import styles from './CumulatedViews.module.scss'
import { CumulatedViewsEmptyState } from './CumulatedViewsEmptyState'

const MONTH_FORMAT = 'LLLL'
const FORMAT_OPTIONS = { locale: fr }

const createMonthAxisFormatter = (firstMonth: string | null) => {
  return (value: string | number): string => {
    const month = format(new Date(value), MONTH_FORMAT, FORMAT_OPTIONS)

    if (month === firstMonth) {
      return ''
    }

    return month.charAt(0).toUpperCase() + month.slice(1)
  }
}

export interface CumulatedViewsProps {
  dailyViews: OffererViewsModel[]
  totalViewsLast30Days: number
}

type XYPoint = { x: string; y: number }

Chart.register(
  Filler,
  LineController,
  LineElement,
  LinearScale,
  PointElement,
  TimeSeriesScale,
  Tooltip
)

export const CumulatedViews = ({
  dailyViews,
  totalViewsLast30Days,
}: CumulatedViewsProps) => {
  const chartRef = useRef<ChartJS<'line', XYPoint[], unknown> | null>(null)

  const hasNoViews =
    dailyViews.length < 2 ||
    dailyViews.every((view) => view.numberOfViews === 0)

  const { recentViews, minViews, maxViews, firstMonth } = useMemo(() => {
    const cutoff = startOfMonth(subMonths(new Date(), 5))
    cutoff.setDate(16)

    const filtered: { date: Date; views: number; rawDate: string }[] = []

    let min = Infinity
    let max = -Infinity

    for (const view of dailyViews) {
      const date = new Date(view.eventDate)
      if (date >= cutoff) {
        const views = view.numberOfViews

        filtered.push({
          date,
          views,
          rawDate: view.eventDate,
        })

        if (views < min) {
          min = views
        }
        if (views > max) {
          max = views
        }
      }
    }

    if (filtered.length === 0) {
      return {
        recentViews: [],
        minViews: 0,
        maxViews: 1000,
        firstMonth: null,
      }
    }

    return {
      recentViews: filtered,
      minViews: min,
      maxViews: max,
      firstMonth: getDateTimeToFrenchText(filtered[0].date, {
        month: 'long',
      }),
    }
  }, [dailyViews])

  const data = useMemo(
    () => ({
      datasets: [
        {
          data: recentViews.map((v) => ({
            x: v.rawDate,
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
    }),
    [recentViews]
  )

  const tickFormatter = useMemo(
    () => createMonthAxisFormatter(firstMonth),
    [firstMonth]
  )

  const stepSize = useMemo(() => {
    const range = maxViews - minViews
    if (range <= 0) {
      return 1
    }

    const roughStep = range / 3
    const magnitude = 10 ** Math.floor(Math.log10(roughStep))
    const niceSteps = [1, 2, 5, 10].map((n) => n * magnitude)

    return niceSteps.find((step) => step >= roughStep) ?? niceSteps.at(-1)!
  }, [minViews, maxViews])

  const options = useMemo(
    () => ({
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
            callback: (value: string | number) => tickFormatter(value),
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
    }),
    [stepSize, firstMonth]
  )

  const chartId = useId()

  return (
    <div className={styles['cumulated-views']}>
      <div className={styles['header']}>
        <h3 className={styles['block-title']}>
          Les statistiques sur l’individuel
        </h3>
        <span className={styles['total-views']}>
          Vos offres individuelles ont été vues{' '}
          {totalViewsLast30Days.toLocaleString('fr-FR')}{' '}
          {pluralizeFr(totalViewsLast30Days, 'vue', 'vues')}
        </span>
      </div>

      {hasNoViews ? (
        <CumulatedViewsEmptyState />
      ) : (
        <div className={styles['chart']}>
          <Line
            ref={chartRef}
            data={data}
            options={options}
            role="img"
            aria-labelledby={`chart-title-${chartId}`}
            aria-details={`chart-description-${chartId}`}
          />
          {/* We wrap in a div, because the .visually-hidden class doesn't work on Chrome on <table> element */}{' '}
          <div className={styles['visually-hidden']}>
            <table id={`chart-description-${chartId}`}>
              <caption id={`chart-title-${chartId}`}>
                Nombre de vues cumulées de toutes vos offres sur les 6 derniers
                mois
              </caption>

              <thead>
                <tr>
                  <th scope="col">Date</th>
                  <th scope="col">Nombre de vues cumulées</th>
                </tr>
              </thead>
              <tbody>
                {dailyViews.map((dailyView) => (
                  <tr key={dailyView.eventDate}>
                    <td>{dailyView.eventDate}</td>
                    <td>{dailyView.numberOfViews}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
