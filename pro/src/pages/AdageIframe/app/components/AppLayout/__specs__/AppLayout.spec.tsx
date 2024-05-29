import { screen } from '@testing-library/react'

import { MARSEILLE_EN_GRAND } from 'pages/AdageIframe/app/constants'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import {
  defaultAdageUser,
  defaultUseInfiniteHitsReturn,
} from 'utils/adageFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

import { AppLayout } from '../AppLayout'

Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: () => ({
    matches: true,
  }),
})

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
    ...(await vi.importActual('react-instantsearch')),
    Configure: vi.fn(() => <div />),
    InstantSearch: vi.fn(({ children }) => <div>{children}</div>),
    useStats: () => ({ nbHits: 1 }),
    useSearchBox: () => ({ refine: vi.fn() }),
    useInfiniteHits: () => ({
      hits: defaultUseInfiniteHitsReturn.hits.slice(0, 1),
    }),
    useInstantSearch: () => ({
      scopedResults: [],
    }),
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

vi.mock('apiClient/api', () => ({
  apiAdage: {
    logHasSeenAllPlaylist: vi.fn(),
    logConsultPlaylistElement: vi.fn(),
    logHasSeenWholePlaylist: vi.fn(),
    newTemplateOffersPlaylist: vi.fn(),
  },
  api: {
    listEducationalDomains: vi.fn(() => [
      { id: 1, name: 'Danse' },
      { id: 2, name: 'Architecture' },
    ]),
  },
}))

vi.mock('hooks/useIsElementVisible', () => ({
  useIsElementVisible: vi.fn(() => [false, false]),
}))

window.scrollTo = vi.fn().mockImplementation(() => {})

const renderAppLayout = (
  options?: RenderWithProvidersOptions,
  user = defaultAdageUser
) => {
  renderWithProviders(
    <AdageUserContextProvider adageUser={{ ...user, offersCount: 1 }}>
      <AppLayout />
    </AdageUserContextProvider>,
    options
  )
}

const featureOverrides = {
  features: ['WIP_ENABLE_MARSEILLE'],
}

describe('AppLayout', () => {
  beforeEach(() => {
    window.IntersectionObserver = vi.fn().mockImplementation(() => ({
      observe: vi.fn(),
      unobserve: vi.fn(),
      disconnect: vi.fn(),
    }))
  })

  it('should redirect to the search page if the user is in Marseille en Grand and if the FF is active', () => {
    renderAppLayout(featureOverrides, {
      ...defaultAdageUser,
      programs: [{ label: '', name: MARSEILLE_EN_GRAND }],
    })

    expect(screen.getByRole('link', { name: 'Rechercher' })).toBeInTheDocument()
  })

  it('should redirect to the discovery page if the user is not in Marseille en Grand and if the FF is active', async () => {
    renderAppLayout(featureOverrides, {
      ...defaultAdageUser,
      programs: [],
    })

    expect(
      await screen.findByRole('heading', {
        name: 'Découvrez la part collective du pass Culture',
      })
    ).toBeInTheDocument()
  })
})
