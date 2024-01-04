import { screen } from '@testing-library/react'
import React from 'react'
import { Configure } from 'react-instantsearch'

import { AdageFrontRoles } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import Notification from 'components/Notification/Notification'
import { defaultCategories } from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { App } from '../App'
import { DEFAULT_GEO_RADIUS } from '../components/OffersInstantSearch/OffersInstantSearch'

vi.mock(
  '../components/OffersInstantSearch/OffersSearch/Autocomplete/Autocomplete',
  () => {
    return {
      Autocomplete: ({ initialQuery }: { initialQuery: string }) => (
        <div>
          <label htmlFor="autocomplete">Autocomplete</label>
          <input
            id="autocomplete"
            value={initialQuery}
            onChange={() => vi.fn()}
          />
          <button onClick={() => vi.fn()}>Rechercher</button>
        </div>
      ),
    }
  }
)

vi.mock('react-instantsearch', async () => {
  return {
    ...((await vi.importActual('react-instantsearch')) ?? {}),
    Configure: vi.fn(() => <div />),
    InstantSearch: vi.fn(({ children }) => <div>{children}</div>),
    useStats: () => ({ nbHits: 1 }),
    useSearchBox: () => ({ refine: vi.fn() }),
    useInfiniteHits: () => ({
      hits: [],
    }),
    useInstantSearch: () => ({ scopedResults: [] }),
    Index: vi.fn(({ children }) => children),
  }
})

vi.mock('pages/AdageIframe/repository/pcapi/pcapi', () => ({
  getEducationalDomains: vi.fn(),
  getFeatures: vi.fn(),
}))

vi.mock('utils/config', async () => {
  return {
    ...((await vi.importActual('utils/config')) ?? {}),
    ALGOLIA_API_KEY: 'adage-api-key',
    ALGOLIA_APP_ID: '1',
    ALGOLIA_COLLECTIVE_OFFERS_INDEX: 'adage-collective-offers',
  }
})

const venue = {
  id: 1436,
  name: 'Librairie de Paris',
  publicName: "Lib de Par's",
  relative: [],
  departementCode: '75',
}

const isDiscoveryActive = {
  features: {
    list: [
      {
        nameKey: 'WIP_ENABLE_DISCOVERY',
        isActive: true,
      },
    ],
    initialized: true,
  },
}

vi.mock('apiClient/api', () => ({
  apiAdage: {
    getEducationalOffersCategories: vi.fn(),
    getVenueById: vi.fn(() => {
      return venue
    }),
    authenticate: vi.fn(),
    getVenueBySiret: vi.fn(() => {
      return venue
    }),
    logSearchButtonClick: vi.fn(),
    logCatalogView: vi.fn(),
    logTrackingFilter: vi.fn(),
    getCollectiveOffer: vi.fn(),
    logHasSeenAllPlaylist: vi.fn(),
  },
}))

vi.mock('@algolia/autocomplete-plugin-query-suggestions', () => {
  return {
    ...vi.importActual('@algolia/autocomplete-plugin-query-suggestions'),
    createQuerySuggestionsPlugin: vi.fn(() => {
      return {
        name: 'querySuggestionName',
        getSources: () => [
          {
            sourceId: '',
            getItems: [],
          },
        ],
      }
    }),
  }
})

const renderApp = (initialEntries = '/', storeOverrides: any = null) => {
  renderWithProviders(
    <>
      <App />
      <Notification />
    </>,
    {
      initialRouterEntries: [initialEntries],
      storeOverrides: storeOverrides,
    }
  )
}

describe('app', () => {
  describe('when is authenticated', () => {
    beforeEach(() => {
      vi.spyOn(apiAdage, 'authenticate').mockResolvedValue({
        role: AdageFrontRoles.REDACTOR,
        uai: 'uai',
        departmentCode: '30',
        institutionName: 'COLLEGE BELLEVUE',
        institutionCity: 'ALES',
      })
      vi.spyOn(apiAdage, 'getEducationalOffersCategories').mockResolvedValue(
        defaultCategories
      )
      window.IntersectionObserver = vi.fn().mockImplementation(() => ({
        observe: vi.fn(),
        unobserve: vi.fn(),
        disconnect: vi.fn(),
      }))
    })

    it('should display venue tag when siret is provided and public name exists', async () => {
      const mockLocation = {
        ...window.location,
        search: '?siret=123456789&venue=1436',
      }

      window.location = mockLocation

      renderApp('/recherche?siret=123456789&venue=1436')

      await screen.findByRole('button', { name: /Lieu : Lib de Par's/ })
    })

    it('should display venue tag when venueId is provided and public name exists', async () => {
      // When
      renderApp('/recherche?venue=1436')

      await screen.findByRole('button', { name: /Lieu : Lib de Par's/ })
    })

    it('should display venue when venueId is provided in url', async () => {
      const mockLocation = {
        ...window.location,
        search: '?venue=1436',
      }

      window.location = mockLocation

      renderApp('/recherche?venue=1436')

      await screen.findByRole('button', { name: /Lieu : Lib de Par's/ })
    })
    it('should display error messagee when venueId does not exist', async () => {
      const mockLocation = {
        ...window.location,
        search: '?venue=999',
      }

      window.location = mockLocation

      vi.spyOn(apiAdage, 'getVenueById').mockRejectedValueOnce(null)

      renderApp('/recherche?venue=999', isDiscoveryActive)

      expect(
        await screen.findByText(
          'Lieu inconnu. Tous les résultats sont affichés.'
        )
      ).toBeInTheDocument()
    })

    it('should add geo location filter when user has latitude and longitude', async () => {
      vi.spyOn(apiAdage, 'authenticate').mockResolvedValueOnce({
        role: AdageFrontRoles.REDACTOR,
        uai: 'uai',
        departmentCode: '30',
        institutionName: 'COLLEGE BELLEVUE',
        institutionCity: 'ALES',
        lat: 48.856614,
        lon: 2.3522219,
      })
      renderApp('/recherche')

      await screen.findByRole('button', { name: 'Rechercher' })

      expect(Configure).toHaveBeenNthCalledWith(
        1,
        expect.objectContaining({
          aroundLatLng: '48.856614, 2.3522219',
          aroundRadius: DEFAULT_GEO_RADIUS,
        }),
        {}
      )
    })

    it('should trigger an error notification when siret is invalid', async () => {
      const mockLocation = {
        ...window.location,
        search: '?siret=123456789',
      }

      window.location = mockLocation

      vi.spyOn(apiAdage, 'getVenueBySiret').mockRejectedValueOnce(null)

      renderApp()

      expect(
        await screen.findByText(
          'Lieu inconnu. Tous les résultats sont affichés.'
        )
      ).toBeInTheDocument()
    })

    it('should trigger an error notification when venue is invalid', async () => {
      const mockLocation = {
        ...window.location,
        search: '?venue=123456789',
      }

      window.location = mockLocation

      vi.spyOn(apiAdage, 'getVenueById').mockRejectedValueOnce(null)

      renderApp()

      expect(
        await screen.findByText(
          'Lieu inconnu. Tous les résultats sont affichés.'
        )
      ).toBeInTheDocument()
    })
  })

  describe('when is not authenticated', () => {
    beforeEach(() => {
      vi.spyOn(apiAdage, 'authenticate').mockRejectedValue(
        'Authentication failed'
      )
    })

    it('should show error page', async () => {
      // When
      renderApp()

      // Then
      const contentTitle = await screen.findByText(
        'Une erreur s’est produite.',
        { selector: 'h1' }
      )
      expect(contentTitle).toBeInTheDocument()
      expect(screen.queryByRole('textbox')).not.toBeInTheDocument()
    })
  })
})
