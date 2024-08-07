import { screen } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import { defaultGetOffererResponseModel } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { StatisticsDashboard } from '../StatisticsDashboard'

vi.mock('apiClient/api', () => ({
  api: {
    getOffererStats: vi.fn(),
    getOffererV2Stats: vi.fn(),
  },
}))

const renderStatisticsDashboard = (
  hasActiveOffer = true,
  features: string[] = [],
  isAdmin = false,
  hasNewNav = false
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
      user: sharedCurrentUserFactory({
        isAdmin,
        navState: {
          newNavDate: hasNewNav ? '2021-01-01' : null,
        },
      }),
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
      screen.getByText('Présence sur l’application pass Culture')
    ).toBeInTheDocument()
    expect(
      await screen.findByText(
        'Créez vos premières offres grand public pour être visible par les bénéficiaires'
      )
    ).toBeInTheDocument()
    expect(screen.getByText('Dernière mise à jour :')).toBeInTheDocument()

    expect(screen.getByText('Vos offres publiées')).toBeInTheDocument()
  })

  it('should render statistics dashboard with statistics coming soon message', async () => {
    renderStatisticsDashboard()

    expect(
      screen.getByText('Présence sur l’application pass Culture')
    ).toBeInTheDocument()
    expect(
      await screen.findByText(
        'Les statistiques de consultation de vos offres seront bientôt disponibles.'
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

    renderStatisticsDashboard()

    expect(
      screen.getByText('Présence sur l’application pass Culture')
    ).toBeInTheDocument()
    expect(
      await screen.findByText('Évolution des consultations de vos offres')
    ).toBeInTheDocument()
    expect(
      screen.queryByText('Vos offres les plus consultées')
    ).not.toBeInTheDocument()
    expect(screen.getByText('Dernière mise à jour :')).toBeInTheDocument()

    expect(screen.getByText('Vos offres publiées')).toBeInTheDocument()
  })

  it('should display the create offer button by default', async () => {
    renderStatisticsDashboard(false)

    expect(await screen.findByText(/Créer une offre/)).toBeInTheDocument()
  })

  it('should display the create offer button if the user is Admin', async () => {
    renderStatisticsDashboard(false, [], true)

    expect(await screen.findByText(/Créer une offre/)).toBeInTheDocument()
  })

  it("should not display the create offer button if the user isn't Admin", async () => {
    renderStatisticsDashboard(false, [], false, true)

    expect(
      await screen.findByText('à destination du grand public')
    ).toBeInTheDocument()
    expect(screen.queryByText(/Créer une offre/)).not.toBeInTheDocument()
  })
})
