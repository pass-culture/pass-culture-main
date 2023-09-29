import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import React from 'react'

import {
  AlgoliaQueryContextProvider,
  FiltersContextProvider,
} from 'pages/AdageIframe/app/providers'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import {
  defaultAdageUser,
  defaultUseInfiniteHitsReturn,
} from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { AppLayout } from '../AppLayout'

vi.mock('apiClient/api', () => ({
  apiAdage: {
    getEducationalOffersCategories: vi.fn(),
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
  it('should render new header if FF is active', async () => {
    renderAppLayout()
    waitForElementToBeRemoved(() => screen.getByTestId('spinner'))

    expect(screen.getByRole('link', { name: 'Rechercher' })).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Pour mon établissement 1' })
    ).toBeInTheDocument()
  })
})
