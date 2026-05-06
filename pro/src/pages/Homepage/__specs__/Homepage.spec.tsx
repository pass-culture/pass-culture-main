import { screen, waitForElementToBeRemoved } from '@testing-library/react'

import { api, apiNew } from '@/apiClient/api'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import { PartnerLayout } from '@/layouts/PartnerLayout/PartnerLayout'

import { Homepage } from '../Homepage'

const homepageRoutes = [
  {
    path: '/',
    Component: PartnerLayout,
    children: [
      {
        path: 'accueil',
        element: <Homepage />,
        handle: { title: 'Espace acteurs culturels' },
      },
    ],
  },
]

const renderHomepage = (options?: RenderWithProvidersOptions) => {
  const user = sharedCurrentUserFactory()
  const { storeOverrides, ...restOptions } = options ?? {}
  renderWithProviders(null, {
    routes: homepageRoutes,
    initialRouterEntries: ['/accueil'],
    user,
    ...restOptions,
    storeOverrides: {
      user: {
        currentUser: user,
        selectedPartnerVenue: defaultGetVenue,
      },
      ...storeOverrides,
    },
  })
}

describe('Homepage', () => {
  beforeEach(() => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [{ id: 1, name: 'Structure 1' }],
      offerersNamesWithPendingValidation: [],
    })
    vi.spyOn(api, 'getOffererV2Stats').mockResolvedValue({
      pendingEducationalOffers: 0,
      pendingPublicOffers: 0,
      publishedEducationalOffers: 0,
      publishedPublicOffers: 0,
    })
    vi.spyOn(api, 'getVenueOffersStats').mockResolvedValue({
      jsonData: { dailyViews: [], topOffers: [], totalViewsLast30Days: 0 },
      venueId: defaultGetVenue.id,
    })
    vi.spyOn(apiNew, 'getHighlights').mockResolvedValue([])
  })

  it('should display the presence section', async () => {
    renderHomepage()

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(
      screen.getByText('Présence sur l’application pass Culture')
    ).toBeInTheDocument()
  })

  describe('highlights', () => {
    it('should display highlights when the selected partner venue can display them', async () => {
      renderHomepage({
        storeOverrides: {
          user: {
            currentUser: sharedCurrentUserFactory(),
            selectedPartnerVenue: {
              ...defaultGetVenue,
              canDisplayHighlights: true,
            },
          },
        },
      })

      expect(
        await screen.findByText('Parcourir les temps forts')
      ).toBeInTheDocument()
    })

    it('should not display highlights when the selected partner venue cannot display them', async () => {
      renderHomepage({
        storeOverrides: {
          user: {
            currentUser: sharedCurrentUserFactory(),
            selectedPartnerVenue: {
              ...defaultGetVenue,
              canDisplayHighlights: false,
            },
          },
        },
      })

      await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

      expect(
        screen.queryByText('Parcourir les temps forts')
      ).not.toBeInTheDocument()
    })
  })
})
