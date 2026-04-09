import { screen, waitFor } from '@testing-library/react'

import { api } from '@/apiClient/api'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { StatisticsDashboard } from '../StatisticsDashboard'

vi.mock('@/apiClient/api', () => ({
  api: {
    getVenueOffersStats: vi.fn(),
  },
}))

const renderStatisticsDashboard = (hasOffers = true, features: string[] = []) =>
  renderWithProviders(
    <StatisticsDashboard
      venue={{
        ...defaultGetVenue,
        hasNonDraftOffers: hasOffers,
      }}
    />,
    {
      user: sharedCurrentUserFactory(),
      features,
    }
  )

describe('StatisticsDashboard', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getVenueOffersStats').mockResolvedValue({
      jsonData: { dailyViews: [], topOffers: [], totalViewsLast30Days: 0 },
      venueId: 1,
    })
  })

  it('should render empty state when offerer has no offers', async () => {
    renderStatisticsDashboard(false)

    expect(
      await screen.findByText(
        'Créez vos premières offres grand public pour être visible par les bénéficiaires'
      )
    ).toBeInTheDocument()
  })

  it('should render statistics dashboard with statistics coming soon message', async () => {
    renderStatisticsDashboard()

    expect(
      await screen.findByText(
        'Les statistiques de consultation de vos offres seront bientôt disponibles.'
      )
    ).toBeInTheDocument()
  })

  it('should not render most viewed offers if there are none', async () => {
    vi.spyOn(api, 'getVenueOffersStats').mockResolvedValue({
      jsonData: {
        dailyViews: [
          { day: '2020-10-10', views: 10 },
          { day: '2020-10-11', views: 20 },
        ],
        topOffers: [],
        totalViewsLast30Days: 0,
      },
      venueId: 1,
    })

    renderStatisticsDashboard()

    await waitFor(() => {
      expect(
        screen.getByRole('heading', {
          name: /Les statistiques sur l'individuel/,
        })
      ).toBeInTheDocument()
    })
    expect(
      screen.queryByText('Vos offres les plus consultées')
    ).not.toBeInTheDocument()
  })
})
