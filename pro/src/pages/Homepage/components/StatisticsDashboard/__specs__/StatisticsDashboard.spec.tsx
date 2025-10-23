import { screen } from '@testing-library/react'

import { api } from '@/apiClient/api'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { StatisticsDashboard } from '../StatisticsDashboard'

vi.mock('@/apiClient/api', () => ({
  api: {
    getOffererStats: vi.fn(),
    getOffererV2Stats: vi.fn(),
  },
}))

const renderStatisticsDashboard = (
  hasActiveOffer = true,
  features: string[] = []
) =>
  renderWithProviders(
    <StatisticsDashboard
      offerer={{
        ...defaultGetOffererResponseModel,
        isValidated: true,
        hasActiveOffer: hasActiveOffer,
      }}
    />,
    {
      user: sharedCurrentUserFactory(),
      features,
    }
  )

describe('StatisticsDashboard', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getOffererStats').mockResolvedValue({
      jsonData: { dailyViews: [], topOffers: [], totalViewsLast30Days: 0 },
      syncDate: null,
      offererId: 1,
    })
    vi.spyOn(api, 'getOffererV2Stats').mockResolvedValue({
      publishedPublicOffers: 1,
      publishedEducationalOffers: 0,
      pendingPublicOffers: 0,
      pendingEducationalOffers: 0,
    })
  })

  it('should render empty state when offerer has no offers', async () => {
    vi.spyOn(api, 'getOffererV2Stats').mockResolvedValueOnce({
      publishedPublicOffers: 0,
      publishedEducationalOffers: 0,
      pendingPublicOffers: 0,
      pendingEducationalOffers: 0,
    })

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
    vi.spyOn(api, 'getOffererStats').mockResolvedValueOnce({
      jsonData: {
        dailyViews: [{ eventDate: '2020-10-10', numberOfViews: 10 }],
        topOffers: [],
        totalViewsLast30Days: 0,
      },
      syncDate: null,
      offererId: 1,
    })

    renderStatisticsDashboard()

    expect(
      await screen.findByText('Évolution des consultations de vos offres')
    ).toBeInTheDocument()
    expect(
      screen.queryByText('Vos offres les plus consultées')
    ).not.toBeInTheDocument()
  })

  it('should display the last sync date', async () => {
    vi.spyOn(api, 'getOffererStats').mockResolvedValueOnce({
      jsonData: {
        dailyViews: [{ eventDate: '2020-10-10', numberOfViews: 10 }],
        topOffers: [],
        totalViewsLast30Days: 0,
      },
      syncDate: '2020-10-10',
      offererId: 1,
    })

    renderStatisticsDashboard()

    expect(
      await screen.findByText('Dernière mise à jour : 10/10/2020 00:00')
    ).toBeInTheDocument()
  })
})
