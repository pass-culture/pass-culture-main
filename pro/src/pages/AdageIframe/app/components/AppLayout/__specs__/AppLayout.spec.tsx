import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import React from 'react'

import {
  AlgoliaQueryContextProvider,
  FiltersContextProvider,
} from 'pages/AdageIframe/app/providers'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import {
  defaultAdageUser,
  defaultCategories,
  defaultUseInfiniteHitsReturn,
} from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { AppLayout } from '../AppLayout'

vi.mock(
  '../../OffersInstantSearch/OffersSearch/Autocomplete/Autocomplete',
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

vi.mock('apiClient/api', () => ({
  apiAdage: {
    getEducationalOffersCategories: vi.fn(() => defaultCategories),
    getVenueById: vi.fn(),
    authenticate: vi.fn(),
    getVenueBySiret: vi.fn(),
    logSearchButtonClick: vi.fn(),
    logCatalogView: vi.fn(),
    getCollectiveOffer: vi.fn(),
  },
}))

vi.mock('react-instantsearch', async () => {
  return {
    ...((await vi.importActual('react-instantsearch')) ?? {}),
    Configure: vi.fn(() => <div />),
    InstantSearch: vi.fn(({ children }) => <div>{children}</div>),
    useStats: () => ({ nbHits: 1 }),
    useSearchBox: () => ({ refine: vi.fn() }),
    useInfiniteHits: () => ({
      hits: defaultUseInfiniteHitsReturn.hits.slice(0, 1),
    }),
  }
})

vi.mock('utils/config', async () => {
  return {
    ...((await vi.importActual('utils/config')) ?? {}),
    ALGOLIA_API_KEY: 'adage-api-key',
    ALGOLIA_APP_ID: '1',
    ALGOLIA_COLLECTIVE_OFFERS_INDEX: 'adage-collective-offers',
  }
})

vi.mock('pages/AdageIframe/repository/pcapi/pcapi', () => ({
  getEducationalDomains: vi.fn(),
  getFeatures: vi.fn(),
}))

const renderAppLayout = (initialRoute = '/') => {
  renderWithProviders(
    <AdageUserContextProvider adageUser={defaultAdageUser}>
      <FiltersContextProvider>
        <AlgoliaQueryContextProvider>
          <AppLayout removeVenueFilter={vi.fn()} venueFilter={null} />
        </AlgoliaQueryContextProvider>
      </FiltersContextProvider>
    </AdageUserContextProvider>,

    { initialRouterEntries: [initialRoute] }
  )
}

describe('AppLayout', () => {
  beforeEach(() => {
    window.IntersectionObserver = vi.fn().mockImplementation(() => ({
      observe: vi.fn(),
      unobserve: vi.fn(),
      disconnect: vi.fn(),
    }))
  })

  it('should render new header if FF is active', async () => {
    renderAppLayout()
    waitForElementToBeRemoved(() => screen.getByTestId('spinner'))

    expect(screen.getByRole('link', { name: 'Rechercher' })).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Pour mon établissement 1' })
    ).toBeInTheDocument()
  })
})
