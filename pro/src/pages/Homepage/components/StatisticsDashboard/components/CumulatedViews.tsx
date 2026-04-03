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
import { useId, useMemo, useRef } from 'react'
import { Line } from 'react-chartjs-2'
import 'chartjs-adapter-date-fns'

import type { VenueDailyViewModel } from '@/apiClient/v1'
import { getDateTimeToFrenchText } from '@/commons/utils/date'

import { buildGraphOptions, computeGraphSteps } from '../statsUtils'
import styles from './CumulatedViews.module.scss'
import { CumulatedViewsEmptyState } from './CumulatedViewsEmptyState'

// TODO (cmoinier 2025-02-18) remove component after switch venue FF

export interface CumulatedViewsProps {
  dailyViews: VenueDailyViewModel[]
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
    dailyViews.length < 2 || dailyViews.every((view) => view.views === 0)

  const { recentViews, minViews, maxViews, firstMonth } = useMemo(() => {
    const cutoff = startOfMonth(subMonths(new Date(), 5))
    cutoff.setDate(16)

    const filtered: { date: Date; views: number; rawDate: string }[] = []

    let min = Infinity
    let max = -Infinity

    for (const view of dailyViews) {
      const date = new Date(view.day)
      if (date >= cutoff) {
        const views = view.views

        filtered.push({
          date,
          views,
          rawDate: view.day,
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

  const chartId = useId()
  const stepSize = useMemo(
    () => computeGraphSteps(maxViews, minViews),
    [minViews, maxViews]
  )
  const graphOptions = useMemo(
    () => buildGraphOptions(stepSize, firstMonth),
    [stepSize, firstMonth]
  )
  return (
    <div className={styles['cumulated-views']}>
      <div className={styles['header']}>
        <h3 className={styles['block-title']}>
          Les statistiques sur l’individuel
        </h3>
        <span className={styles['total-views']}>
          Vos offres individuelles ont été vues{' '}
          {totalViewsLast30Days.toLocaleString('fr-FR')} fois
        </span>
      </div>

      {hasNoViews ? (
        <CumulatedViewsEmptyState />
      ) : (
        <div className={styles['chart']}>
          <Line
            ref={chartRef}
            data={data}
            options={graphOptions}
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
                  <tr key={dailyView.day}>
                    <td>{dailyView.day}</td>
                    <td>{dailyView.views}</td>
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
