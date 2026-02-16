import { screen } from '@testing-library/react'

import { api } from '@/apiClient/api'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { VenueStatisticsDashboard } from '../VenueStatisticsDashboard'

vi.mock('@/apiClient/api', () => ({
  api: {
    getVenueOffersStats: vi.fn(),
  },
}))

const renderVenueStatisticsDashboard = (
  hasOffers = true,
  features: string[] = []
) =>
  renderWithProviders(
    <VenueStatisticsDashboard
      venue={{
        ...defaultGetVenue,
        hasOffers: hasOffers,
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
      jsonData: { monthlyViews: [], topOffers: [], totalViewsLast30Days: 0 },
      venueId: 1,
    })
  })

  it('should render empty state when offerer has no offers', async () => {
    renderVenueStatisticsDashboard(false)

    expect(
      await screen.findByText(
        'Créez vos premières offres grand public pour être visible par les bénéficiaires'
      )
    ).toBeInTheDocument()
  })

  it('should render statistics dashboard with statistics coming soon message', async () => {
    renderVenueStatisticsDashboard()

    expect(
      await screen.findByText(
        'Les statistiques de consultation de vos offres seront bientôt disponibles.'
      )
    ).toBeInTheDocument()
  })

  it('should not render most viewed offers if there are none', async () => {
    vi.spyOn(api, 'getVenueOffersStats').mockResolvedValueOnce({
      jsonData: {
        monthlyViews: [{ month: 8, views: 10 }],
        topOffers: [],
        totalViewsLast30Days: 0,
      },
      venueId: 1,
    })

    renderVenueStatisticsDashboard()

    expect(
      await screen.findByRole('heading', {
        name: /Les statistiques sur l’individuel/,
      })
    ).toBeInTheDocument()
    expect(
      screen.queryByText('Vos offres les plus consultées')
    ).not.toBeInTheDocument()
  })

  it('should render monthlyViews graph if there is data', async () => {
    vi.spyOn(api, 'getVenueOffersStats').mockResolvedValueOnce({
      jsonData: {
        monthlyViews: [
          { month: 8, views: 10 },
          { month: 9, views: 10 },
          { month: 10, views: 10 },
        ],
        topOffers: [],
        totalViewsLast30Days: 0,
      },
      venueId: 1,
    })

    renderVenueStatisticsDashboard()

    expect(
      await screen.findByText(
        'Nombre de vues cumulées de toutes vos offres sur les 6 derniers mois'
      )
    ).toBeInTheDocument()
  })
})
