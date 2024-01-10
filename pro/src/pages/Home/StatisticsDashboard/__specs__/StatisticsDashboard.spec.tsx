import { screen } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import { defaultGetOffererResponseModel } from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  StatisticsDashboard,
  StatisticsDashboardProps,
} from '../StatisticsDashboard'

vi.mock('apiClient/api', () => ({
  api: {
    getOffererStats: vi.fn(),
    getOffererV2Stats: vi.fn(),
  },
}))

const renderStatisticsDashboard = (
  props: Partial<StatisticsDashboardProps> = {}
) =>
  renderWithProviders(
    <StatisticsDashboard
      offerer={{ ...defaultGetOffererResponseModel, isValidated: true }}
      {...props}
    />
  )

describe('StatisticsDashboard', () => {
  it('should render empty state when no statistics', async () => {
    vi.spyOn(api, 'getOffererStats').mockResolvedValueOnce({
      jsonData: { dailyViews: [], topOffers: [], totalViewsLast30Days: 0 },
      syncDate: null,
      offererId: 1,
    })
    vi.spyOn(api, 'getOffererV2Stats').mockResolvedValueOnce({
      publishedPublicOffers: 0,
      publishedEducationalOffers: 0,
      pendingPublicOffers: 0,
      pendingEducationalOffers: 0,
    })

    renderStatisticsDashboard()

    expect(screen.getByText('Présence sur le pass Culture')).toBeInTheDocument()
    expect(
      await screen.findByText(
        'Créez vos premières offres grand public pour être visible par les bénéficiaires'
      )
    ).toBeInTheDocument()
    expect(screen.getByText('Dernière mise à jour :')).toBeInTheDocument()

    expect(screen.getByText('Vos offres publiées')).toBeInTheDocument()
  })

  it('should not render most viewed offers if there are none', async () => {
    vi.spyOn(api, 'getOffererStats').mockResolvedValueOnce({
      jsonData: {
        dailyViews: [{ eventDate: '2020-10-10', numberOfViews: 10 }],
        topOffers: [],
        totalViewsLast30Days: 0,
      },
      syncDate: null,
      offererId: 1,
    })
    vi.spyOn(api, 'getOffererV2Stats').mockResolvedValueOnce({
      publishedPublicOffers: 1,
      publishedEducationalOffers: 0,
      pendingPublicOffers: 0,
      pendingEducationalOffers: 0,
    })

    renderStatisticsDashboard()

    expect(screen.getByText('Présence sur le pass Culture')).toBeInTheDocument()
    expect(
      await screen.findByText('Évolution des consultations de vos offres')
    ).toBeInTheDocument()
    expect(
      screen.queryByText('Vos offres les plus consultées')
    ).not.toBeInTheDocument()
    expect(screen.getByText('Dernière mise à jour :')).toBeInTheDocument()

    expect(screen.getByText('Vos offres publiées')).toBeInTheDocument()
  })
})
