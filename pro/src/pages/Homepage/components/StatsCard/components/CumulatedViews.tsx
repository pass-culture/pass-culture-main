import {
  BarElement,
  CategoryScale,
  Chart,
  type Chart as ChartJS,
  Filler,
  LinearScale,
  TimeSeriesScale,
  Tooltip,
} from 'chart.js'
import { useId, useMemo, useRef, useState } from 'react'
import { Bar } from 'react-chartjs-2'
import 'chartjs-adapter-date-fns'

import { noop } from 'commons/utils/noop'
import { ToggleButtonGroup } from 'pages/Homepage/components/StatsCard/components/ToggleButtonGroup/ToggleButtonGroup'
import { Table, TableVariant } from 'ui-kit/Table/Table'

import { getDateTimeToFrenchText } from '@/commons/utils/date'
import strokeSignalIcon from '@/icons/stroke-signal.svg'
import strokeTableIcon from '@/icons/stroke-table.svg'

import type {
  VenueMonthlyViewModel,
  VenueOffersPeriodStatsModel,
} from 'apiClient/v1'
import { buildDatasets, buildV2GraphOptions, computeGraphSteps } from '../utils'
import styles from './CumulatedViews.module.scss'

export interface CumulatedViewsProps {
  periodStats?: VenueOffersPeriodStatsModel
}

type XYPoint = { x: string; y: number }

Chart.register(
  CategoryScale,
  BarElement,
  LinearScale,
  TimeSeriesScale,
  Tooltip,
  Filler
)

export const CumulatedViews = ({ periodStats }: CumulatedViewsProps) => {
  const chartRef = useRef<ChartJS<'bar', XYPoint[], unknown> | null>(null)
  const [selectedTab, setSelectedTab] = useState<'chart' | 'table'>('chart')

  const chartContainerId = useId()

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

  const stepSize = useMemo(
    () => computeGraphSteps(maxViews, minViews),
    [minViews, maxViews]
  )
  const graphOptions = useMemo(
    () => buildV2GraphOptions(stepSize, Math.ceil(maxViews / 10) * 10),
    [stepSize, firstMonth, periodStats]
  )

  const columns = [
    {
      id: 'month',
      label: 'Mois',
      render: (model: VenueMonthlyViewModel) => (
        <span>
          {getDateTimeToFrenchText(new Date(model.month), {
            month: 'long',
          })}
        </span>
      ),
    },
    {
      id: 'views',
      label: 'Nombre de consultations',
      render: (model: VenueMonthlyViewModel) => <span>{model.views}</span>,
    },
  ]
  const left = {
    id: useId(),
    label: 'Graphique',
    icon: strokeSignalIcon,
    handleClick: () => setSelectedTab('chart'),
  }
  const right = {
    id: useId(),
    label: 'Tableau',
    handleClick: () => setSelectedTab('table'),
    icon: strokeTableIcon,
  }
  return (
    <div className={styles['cumulated-views']}>
      <ToggleButtonGroup
        left={left}
        right={right}
        selected="left"
        controls={chartContainerId}
      />
      <div className={styles['chart']} id={chartContainerId}>
        {selectedTab === 'chart' && (
          <Bar
            ref={chartRef}
            data={data}
            options={graphOptions}
            role="tabpanel"
            aria-labelledby={left.id}
            aria-hidden={true}
          />
        )}
        {selectedTab === 'table' && (
          <div role="tabpanel" aria-labelledby={right.id}>
            <Table
              title={`Nombre de vues cumulées de toutes vos offres sur les ${periodStats?.viewsByMonth.length ?? 0} derniers mois`}
              columns={columns}
              data={(
                periodStats?.viewsByMonth.map((i) => ({ ...i, id: i.month })) ??
                []
              ).reverse()}
              isLoading={false}
              variant={TableVariant.COLLAPSE}
              noResult={{
                message: '',
                subtitle: undefined,
                resetMessage: undefined,
                onFilterReset: noop,
              }}
              noData={{
                hasNoData: false,
                message: {
                  icon: '',
                  title: '',
                  subtitle: undefined,
                  cta: undefined,
                },
              }}
            />
          </div>
        )}
      </div>
    </div>
  )
}
