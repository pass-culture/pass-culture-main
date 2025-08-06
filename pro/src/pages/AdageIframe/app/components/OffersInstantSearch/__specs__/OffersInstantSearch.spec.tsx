import { screen, waitForElementToBeRemoved } from '@testing-library/react'

import { apiAdage } from '@/apiClient/api'
import { defaultAdageUser } from '@/commons/utils/factories/adageFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { Notification } from '@/components/Notification/Notification'
import { AdageUserContextProvider } from '@/pages/AdageIframe/app/providers/AdageUserContext'

import { OffersInstantSearch } from '../OffersInstantSearch'
import * as utils from '../utils'

const venue = {
  id: 1436,
  name: 'Librairie de Paris',
  publicName: "Librairie de Par's",
  relative: [],
  departementCode: '75',
}

vi.mock('@/apiClient/api', () => ({
  apiAdage: {
    getVenueById: vi.fn(() => {
      return venue
    }),
    getVenueBySiret: vi.fn(() => {
      return venue
    }),
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
      hits: [],
    }),
    useInstantSearch: () => ({ scopedResults: [] }),
    Index: vi.fn(() => <div />),
  }
})

function renderOffersInstantSearch() {
  renderWithProviders(
    <AdageUserContextProvider adageUser={defaultAdageUser}>
      <OffersInstantSearch />
      <Notification />
    </AdageUserContextProvider>
  )
}

describe('OffersInstantSearch', () => {
  beforeEach(() => {
    window.IntersectionObserver = vi.fn().mockImplementation(() => ({
      observe: vi.fn(),
      unobserve: vi.fn(),
      disconnect: vi.fn(),
    }))
  })

  it('should show an error message when the venue id is invalid', async () => {
    const mockLocation = {
      ...window.location,
      search: '?venue=1436',
    }
    window.location = mockLocation as string & Location

    vi.spyOn(apiAdage, 'getVenueById').mockRejectedValueOnce(null)

    renderOffersInstantSearch()

    expect(
      await screen.findByText('Lieu inconnu. Tous les résultats sont affichés.')
    ).toBeInTheDocument()
  })

  it('should show an error message when the siret is invalid', async () => {
    const mockLocation = {
      ...window.location,
      search: '?siret=1436',
    }
    window.location = mockLocation as string & Location

    vi.spyOn(apiAdage, 'getVenueBySiret').mockRejectedValueOnce(null)

    renderOffersInstantSearch()

    expect(
      await screen.findByText('Lieu inconnu. Tous les résultats sont affichés.')
    ).toBeInTheDocument()
  })

  it('should filter on the venue specified in the url', async () => {
    const mockLocation = {
      ...window.location,
      search: '?venue=1436',
    }
    window.location = mockLocation as string & Location

    const setFiltersSpy = vi
      .spyOn(utils, 'adageFiltersToFacetFilters')
      .mockReturnValue({ queryFilters: [], filtersKeys: [] })

    renderOffersInstantSearch()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(setFiltersSpy).toHaveBeenCalledOnce()
  })
})
