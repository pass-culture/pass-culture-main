import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from '@/commons/utils/renderWithProviders'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import {
  CollectiveOffersSearchFilters,
  CollectiveOffersSearchFiltersProps,
} from '../CollectiveOffersSearchFilters'
import {
  ALL_OFFERERS_OPTION,
  ALL_VENUES_OPTION,
  DEFAULT_COLLECTIVE_SEARCH_FILTERS,
} from '@/commons/core/Offers/constants'
import { screen } from '@testing-library/react'
import {
  defaultGetOffererResponseModel,
  venueListItemFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { VenueListItemResponseModel } from '@/apiClient/v1'

let mockVenuesResponse: { venues: VenueListItemResponseModel[] } = {
  venues: [
    venueListItemFactory({
      id: 1,
      name: 'First Venue',
      isPermanent: true,
      hasCreatedOffer: true,
    }),
    venueListItemFactory({
      id: 2,
      name: 'Second Venue',
      isPermanent: true,
      hasCreatedOffer: true,
    }),
  ],
}

vi.mock('@/apiClient/api', () => {
  return {
    api: {
      listOfferersNames: vi.fn().mockReturnValue({}),
      deleteDraftOffers: vi.fn(),
      getVenues: vi.fn(() => mockVenuesResponse),
    },
  }
})

const renderCollectiveOffersSearchFilters = (
  props: CollectiveOffersSearchFiltersProps,
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(<CollectiveOffersSearchFilters {...props} />, {
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
      },
      offerer: currentOffererFactory(),
    },
    ...options,
  })
}

describe('CollectiveOffersSearchFilters', () => {
  let props = {
    hasFilters: true,
    applyFilters: () => {},
    offerer: { ...defaultGetOffererResponseModel },
    selectedFilters: DEFAULT_COLLECTIVE_SEARCH_FILTERS,
    setSelectedFilters: () => {},
    disableAllFilters: false,
    resetFilters: () => {},
  }

  beforeEach(() => {
    mockVenuesResponse.venues = [
      venueListItemFactory({
        id: 1,
        name: 'First Venue',
        isPermanent: true,
        hasCreatedOffer: true,
      }),
      venueListItemFactory({
        id: 2,
        name: 'Second Venue',
        isPermanent: true,
        hasCreatedOffer: true,
      }),
    ]
  })

  it('should render venue filter with default option selected and given venues as options', async () => {
    const expectedSelectOptions = [
      {
        id: [ALL_VENUES_OPTION.value],
        value: ALL_OFFERERS_OPTION.label,
      },
      { id: 1, value: 'First Venue' },
      {
        id: 2,
        value: 'Second Venue',
      },
    ]

    renderCollectiveOffersSearchFilters(props)

    const defaultOption = await screen.findByDisplayValue(
      expectedSelectOptions[0].value
    )
    expect(defaultOption).toBeInTheDocument()

    const firstVenueOption = await screen.findByRole('option', {
      name: expectedSelectOptions[1].value,
    })
    expect(firstVenueOption).toBeInTheDocument()

    const secondVenueOption = await screen.findByRole('option', {
      name: expectedSelectOptions[2].value,
    })
    expect(secondVenueOption).toBeInTheDocument()
  })

  it('should render venue filter with given venue selected', async () => {
    const expectedSelectOptions = [{ id: 1, value: 'First Venue' }]
    const filters = {
      ...DEFAULT_COLLECTIVE_SEARCH_FILTERS,
      venueId: '1',
    }

    renderCollectiveOffersSearchFilters({
      ...props,
      selectedFilters: filters,
    })

    const venueSelect = await screen.findByDisplayValue(
      expectedSelectOptions[0].value
    )
    expect(venueSelect).toBeInTheDocument()
  })
})
