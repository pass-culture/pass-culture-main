import { screen } from '@testing-library/react'
import { add, format, subMonths } from 'date-fns'

import { FORMAT_ISO_DATE_ONLY } from '@/commons/utils/date'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  CumulatedViews,
  type CumulatedViewsProps,
} from '../components/CumulatedViews'

const renderCumulatedViews = (props: CumulatedViewsProps) =>
  renderWithProviders(<CumulatedViews {...props} />)

describe('CumulatedViews', () => {
  it('should render empty state when no views data', () => {
    renderCumulatedViews({ dailyViews: [], totalViewsLast30Days: 0 })

    expect(
      screen.getByText(
        'Vos offres n\u2019ont pas encore été découvertes par les bénéficiaires'
      )
    ).toBeVisible()
  })

  it('should render empty state when 0 views in the past 6 months', () => {
    const sixMonthsWithNoViews = Array.from(Array(180)).map((_key, index) => ({
      numberOfViews: 0,
      eventDate: format(
        add(new Date('2021-01-01'), { days: index }),
        FORMAT_ISO_DATE_ONLY
      ),
    }))

    renderCumulatedViews({
      dailyViews: sixMonthsWithNoViews,
      totalViewsLast30Days: 0,
    })

    expect(
      screen.getByText(
        'Vos offres n\u2019ont pas encore été découvertes par les bénéficiaires'
      )
    ).toBeVisible()
  })

  it('should render graph and accessible table if data is present', () => {
    const dailyViews = Array.from(Array(180)).map((_key, index) => ({
      numberOfViews: index,
      eventDate: format(
        add(new Date('2021-01-01'), { days: index }),
        FORMAT_ISO_DATE_ONLY
      ),
    }))

    renderCumulatedViews({ dailyViews, totalViewsLast30Days: 0 })

    expect(
      screen.getByText(
        'Nombre de vues cumulées de toutes vos offres sur les 6 derniers mois'
      )
    ).toBeVisible()
  })

  it('should render chart with recent data within 6 months', () => {
    const today = new Date()
    const start = subMonths(today, 4)

    const dailyViews = Array.from({ length: 120 }, (_, index) => ({
      numberOfViews: (index + 1) * 10,
      eventDate: format(add(start, { days: index }), FORMAT_ISO_DATE_ONLY),
    }))

    renderCumulatedViews({ dailyViews, totalViewsLast30Days: 0 })

    expect(screen.getByRole('img')).toBeInTheDocument()
    expect(screen.getByRole('table')).toBeInTheDocument()
  })

  it('should render table rows for each data point', () => {
    const today = new Date()
    const start = subMonths(today, 1)

    const dailyViews = Array.from({ length: 10 }, (_, index) => ({
      numberOfViews: 100 + index,
      eventDate: format(add(start, { days: index }), FORMAT_ISO_DATE_ONLY),
    }))

    renderCumulatedViews({ dailyViews, totalViewsLast30Days: 0 })

    const rows = screen.getAllByRole('row')

    expect(rows).toHaveLength(11)
  })

  it('should render chart when all views have the same value', () => {
    const today = new Date()
    const start = subMonths(today, 2)

    const dailyViews = Array.from({ length: 30 }, (_, index) => ({
      numberOfViews: 500,
      eventDate: format(add(start, { days: index }), FORMAT_ISO_DATE_ONLY),
    }))

    renderCumulatedViews({ dailyViews, totalViewsLast30Days: 0 })

    expect(screen.getByRole('img')).toBeInTheDocument()
  })
})
