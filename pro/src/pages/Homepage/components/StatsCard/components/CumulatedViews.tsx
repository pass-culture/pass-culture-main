import {
  BarElement,
  CategoryScale,
  Chart,
  type Chart as ChartJS,
  LinearScale,
  TimeSeriesScale,
  Tooltip,
} from 'chart.js'
import { useId, useMemo, useRef } from 'react'
import { Bar } from 'react-chartjs-2'
import 'chartjs-adapter-date-fns'

import { getDateTimeToFrenchText } from '@/commons/utils/date'

import type { VenueOffersPeriodStatsModel } from 'apiClient/v1'
import { buildDatasets, buildV2GraphOptions, computeGraphSteps } from '../utils'
import styles from './CumulatedViews.module.scss'

export interface CumulatedViewsProps {
  periodStats?: VenueOffersPeriodStatsModel
}

type XYPoint = { x: string; y: number }

Chart.register(CategoryScale, BarElement, LinearScale, TimeSeriesScale, Tooltip)

export const CumulatedViews = ({ periodStats }: CumulatedViewsProps) => {
  const chartRef = useRef<ChartJS<'bar', XYPoint[], unknown> | null>(null)

  const { recentViews, minViews, maxViews, firstMonth } = useMemo(() => {
    const filtered: { date: Date; views: number; rawDate: string }[] = []

    let min = Infinity
    let max = -Infinity

    for (const view of periodStats?.viewsByMonth ?? []) {
      const date = new Date(view.month)
      const views = view.views

      filtered.push({
        date,
        views,
        rawDate: view.month,
      })

      if (views < min) {
        min = views
      }
      if (views > max) {
        max = views
      }
    }

    const hasNoViews = filtered.every((month) => month.views === 0)

    return {
      recentViews: filtered,
      minViews: hasNoViews ? 0 : min,
      maxViews: hasNoViews ? 10 : max,
      firstMonth: filtered[0]
        ? getDateTimeToFrenchText(filtered[0].date, {
            month: 'long',
          })
        : '',
    }
  }, [periodStats?.viewsByMonth])

  const data = useMemo(() => buildDatasets(recentViews, true), [recentViews])

  const chartId = useId()
  const stepSize = useMemo(
    () => computeGraphSteps(maxViews, minViews),
    [minViews, maxViews]
  )
  const graphOptions = useMemo(
    () => buildV2GraphOptions(stepSize, Math.ceil(maxViews / 10) * 10),
    [stepSize, firstMonth, periodStats]
  )

  return (
    <div className={styles['cumulated-views']}>
      <div className={styles['chart']}>
        {/* The visually-hidden table below is the accessible equivalent of this chart,
              so the chart itself is hidden from assistive technologies to avoid
              announcing the same data twice. */}
        <Bar
          ref={chartRef}
          data={data}
          options={graphOptions}
          role="img"
          aria-hidden={true}
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
              {periodStats?.viewsByMonth.map((dailyView) => (
                <tr key={dailyView.month}>
                  <td>{dailyView.month}</td>
                  <td>{dailyView.views}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
