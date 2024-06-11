import { screen } from '@testing-library/react'
import React from 'react'
import { Configure } from 'react-instantsearch'

import { AdageFrontRoles } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { Notification } from 'components/Notification/Notification'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

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

window.scrollTo = vi.fn().mockImplementation(() => {})

vi.mock('react-instantsearch', async () => {
  return {
    ...(await vi.importActual('react-instantsearch')),
    Configure: vi.fn(() => <div />),
    InstantSearch: vi.fn(({ children }) => <div>{children}</div>),
    useStats: () => ({ nbHits: 1 }),
    useSearchBox: () => ({ refine: vi.fn() }),
    useInfiniteHits: () => ({
      currentPageHits: [],
    }),
    useInstantSearch: () => ({ scopedResults: [] }),
    Index: vi.fn(({ children }) => children),
  }
})

vi.mock('utils/config', async () => {
  return {
    ...(await vi.importActual('utils/config')),
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

Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: () => ({
    matches: false,
    addListener: vi.fn(),
    removeListener: vi.fn(),
  }),
})

const renderApp = (options?: RenderWithProvidersOptions) => {
  renderWithProviders(
    <>
      <App />
      <Notification />
    </>,
    {
      initialRouterEntries:
        options?.initialRouterEntries ?? options?.initialRouterEntries,
      storeOverrides: options?.storeOverrides,
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

      renderApp({
        initialRouterEntries: ['/recherche?siret=123456789&venue=1436'],
      })

      await screen.findByRole('button', { name: /Lieu : Lib de Par's/ })
    })

    it('should display venue tag when venueId is provided and public name exists', async () => {
      // When
      renderApp({
        initialRouterEntries: ['/recherche?venue=1436'],
      })

      await screen.findByRole('button', { name: /Lieu : Lib de Par's/ })
    })

    it('should display venue when venueId is provided in url', async () => {
      const mockLocation = {
        ...window.location,
        search: '?venue=1436',
      }

      window.location = mockLocation

      renderApp({
        initialRouterEntries: ['/recherche?venue=1436'],
      })

      await screen.findByRole('button', { name: /Lieu : Lib de Par's/ })
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
      renderApp({
        initialRouterEntries: ['/recherche'],
      })

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
        'Une erreur s’est produite',
        { selector: 'h1' }
      )
      expect(contentTitle).toBeInTheDocument()
      expect(screen.queryByRole('textbox')).not.toBeInTheDocument()
    })
  })
})
