import { screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  VenueCumulatedViews,
  type VenueCumulatedViewsProps,
} from '../components/VenueCumulatedViews'

const renderVenueCumulatedViews = (props: VenueCumulatedViewsProps) =>
  renderWithProviders(<VenueCumulatedViews {...props} />)

describe('CumulatedViews', () => {
  it('should render empty state when no views data', () => {
    renderVenueCumulatedViews({ monthlyViews: [], totalViewsLast30Days: 0 })

    expect(
      screen.getByText(
        'Vos offres n’ont pas encore été découvertes par les bénéficiaires'
      )
    ).toBeInTheDocument()
  })

  it('should render empty state when 0 views in the past 6 months', () => {
    const sixMonthsWithNoViews = Array.from(Array(6)).map((_key, index) => ({
      views: 0,
      month: index,
    }))

    renderVenueCumulatedViews({
      monthlyViews: sixMonthsWithNoViews,
      totalViewsLast30Days: 0,
    })

    expect(
      screen.getByText(
        'Vos offres n’ont pas encore été découvertes par les bénéficiaires'
      )
    ).toBeInTheDocument()
  })

  it('should render graph and accessible table if data is present', () => {
    const monthlyViews = Array.from(Array(6)).map((_key, index) => ({
      views: index,
      month: index,
    }))

    renderVenueCumulatedViews({ monthlyViews, totalViewsLast30Days: 340 })

    expect(
      screen.getByText(
        'Nombre de vues cumulées de toutes vos offres sur les 6 derniers mois'
      )
    ).toBeInTheDocument()
  })
})
