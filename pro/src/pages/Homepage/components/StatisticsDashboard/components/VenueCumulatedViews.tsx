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
import { useId, useMemo, useRef } from 'react'
import { Line } from 'react-chartjs-2'
import 'chartjs-adapter-date-fns'

import type { VenueMonthlyViewModel } from '@/apiClient/v1'
import { mapMonthNumberToFrench } from '@/commons/utils/date'
import {
  buildDatasets,
  buildGraphOptions,
  buildMonthlyViews,
  computeGraphSteps,
} from '@/pages/Homepage/components/StatisticsDashboard/statsUtils'

import styles from './CumulatedViews.module.scss'
import { CumulatedViewsEmptyState } from './CumulatedViewsEmptyState'

export interface VenueCumulatedViewsProps {
  monthlyViews: VenueMonthlyViewModel[]
  totalViewsLast30Days: number
}

type XYPoint = { x: Date; y: number }

Chart.register(
  Filler,
  LineController,
  LineElement,
  LinearScale,
  PointElement,
  TimeSeriesScale,
  Tooltip
)

export const VenueCumulatedViews = ({
  monthlyViews,
  totalViewsLast30Days,
}: VenueCumulatedViewsProps) => {
  const chartRef = useRef<ChartJS<'line', XYPoint[], unknown> | null>(null)

  const hasNoViews =
    monthlyViews.length < 2 || monthlyViews.every((view) => view.views === 0)

  const { recentViews, minViews, maxViews } = useMemo(() => {
    return buildMonthlyViews(monthlyViews)
  }, [monthlyViews])

  const data = useMemo(() => buildDatasets(recentViews), [recentViews])

  const chartId = useId()
  const stepSize = useMemo(
    () => computeGraphSteps(maxViews, minViews),
    [minViews, maxViews]
  )
  const graphOptions = useMemo(
    () => buildGraphOptions(stepSize, null),
    [stepSize]
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
                {monthlyViews.map((monthlyView) => (
                  <tr key={monthlyView.month}>
                    <td>{mapMonthNumberToFrench(monthlyView.month)}</td>
                    <td>{monthlyView.views}</td>
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
