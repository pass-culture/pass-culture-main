import { screen } from '@testing-library/react'
import { add, format } from 'date-fns'

import { FORMAT_ISO_DATE_ONLY } from '@/commons/utils/date'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  CumulatedViews,
  CumulatedViewsProps,
} from '../components/CumulatedViews'

const renderCumulatedViews = (props: CumulatedViewsProps) =>
  renderWithProviders(<CumulatedViews {...props} />)

describe('CumulatedViews', () => {
  it('should render empty state when no views data', () => {
    renderCumulatedViews({ dailyViews: [] })

    expect(
      screen.getByText(
        'Vos offres n’ont pas encore été découvertes par les bénéficiaires'
      )
    ).toBeInTheDocument()
  })

  it('should render empty state when 0 views in the past 6 months', () => {
    const sixMonthsWithNoViews = Array.from(Array(180)).map((key, index) => ({
      numberOfViews: 0,
      eventDate: format(
        add(new Date('2021-01-01'), { days: index }),
        FORMAT_ISO_DATE_ONLY
      ),
    }))

    renderCumulatedViews({ dailyViews: sixMonthsWithNoViews })

    expect(
      screen.getByText(
        'Vos offres n’ont pas encore été découvertes par les bénéficiaires'
      )
    ).toBeInTheDocument()
  })

  it('should render graph and accessible table if data is present', () => {
    const dailyViews = Array.from(Array(180)).map((key, index) => ({
      numberOfViews: index,
      eventDate: format(
        add(new Date('2021-01-01'), { days: index }),
        FORMAT_ISO_DATE_ONLY
      ),
    }))

    renderCumulatedViews({ dailyViews })

    expect(
      screen.getByText(
        'Nombre de vues cumulées de toutes vos offres sur les 6 derniers mois'
      )
    ).toBeInTheDocument()
  })
})
