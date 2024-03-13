import { screen, waitFor } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import { defaultGetOffererResponseModel } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

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
      storeOverrides: {
        user: {
          currentUser: {
            id: 12,
            isAdmin,
            navState: {
              newNavDate: hasNewNav ? '2021-01-01' : null,
            },
          },
        },
      },
      features,
    }
  )

describe('StatisticsDashboard', () => {
  it('should render empty state when offerer has no offers', async () => {
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

    renderStatisticsDashboard(false)

    expect(screen.getByText('Présence sur le pass Culture')).toBeInTheDocument()
    expect(
      await screen.findByText(
        'Créez vos premières offres grand public pour être visible par les bénéficiaires'
      )
    ).toBeInTheDocument()
    expect(screen.getByText('Dernière mise à jour :')).toBeInTheDocument()

    expect(screen.getByText('Vos offres publiées')).toBeInTheDocument()
  })

  it('should render statistics dashboard with statistics coming soon message', async () => {
    vi.spyOn(api, 'getOffererStats').mockResolvedValueOnce({
      jsonData: { dailyViews: [], topOffers: [], totalViewsLast30Days: 0 },
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

  it('should display the create offer button by default', () => {
    renderStatisticsDashboard(false)

    waitFor(() => {
      expect(screen.getByText(/Créer une offre/)).toBeInTheDocument()
    })
  })

  it('should display the create offer button with the WIP_ENABLE_PRO_SIDE_NAV FF enabled and the user is Admin', () => {
    renderStatisticsDashboard(false, ['WIP_ENABLE_PRO_SIDE_NAV'], true)

    expect(screen.getByText(/Créer une offre/)).toBeInTheDocument()
  })

  it("should not display the create offer button with the WIP_ENABLE_PRO_SIDE_NAV FF enabled and the user isn't Admin", () => {
    renderStatisticsDashboard(false, ['WIP_ENABLE_PRO_SIDE_NAV'], false, true)

    expect(screen.queryByText(/Créer une offre/)).not.toBeInTheDocument()
  })
})
