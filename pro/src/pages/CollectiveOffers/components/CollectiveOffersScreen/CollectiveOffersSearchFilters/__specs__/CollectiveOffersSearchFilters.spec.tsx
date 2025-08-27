import { screen } from '@testing-library/react'

import type { VenueListItemResponseModel } from '@/apiClient/v1'
import {
  ALL_OFFERERS_OPTION,
  ALL_VENUES_OPTION,
  DEFAULT_COLLECTIVE_SEARCH_FILTERS,
} from '@/commons/core/Offers/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import {
  defaultGetOffererResponseModel,
  makeVenueListItem,
} from '@/commons/utils/factories/individualApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import {
  CollectiveOffersSearchFilters,
  type CollectiveOffersSearchFiltersProps,
} from '../CollectiveOffersSearchFilters'

const mockVenuesResponse: { venues: VenueListItemResponseModel[] } = {
  venues: [
    makeVenueListItem({
      id: 1,
      name: 'First Venue',
      isPermanent: true,
      hasCreatedOffer: true,
    }),
    makeVenueListItem({
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

vi.mock('@/commons/hooks/useActiveFeature', () => ({
  useActiveFeature: vi.fn(),
}))

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

const baseProps = {
  hasFilters: true,
  applyFilters: () => {},
  offerer: { ...defaultGetOffererResponseModel },
  selectedFilters: DEFAULT_COLLECTIVE_SEARCH_FILTERS,
  setSelectedFilters: () => {},
  disableAllFilters: false,
  resetFilters: () => {},
}

const expectedVenueSelectOptions = [
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

const selectedVenueFilters = {
  ...DEFAULT_COLLECTIVE_SEARCH_FILTERS,
  venueId: '1',
}

describe('CollectiveOffersSearchFilters', () => {
  it('should render venue filter with default option selected and given venues as options', async () => {
    renderCollectiveOffersSearchFilters(baseProps)

    const defaultOption = await screen.findByDisplayValue(
      expectedVenueSelectOptions[0].value
    )
    expect(defaultOption).toBeInTheDocument()

    const firstVenueOption = await screen.findByRole('option', {
      name: expectedVenueSelectOptions[1].value,
    })
    expect(firstVenueOption).toBeInTheDocument()

    const secondVenueOption = await screen.findByRole('option', {
      name: expectedVenueSelectOptions[2].value,
    })
    expect(secondVenueOption).toBeInTheDocument()
  })

  it('should render venue filter with given venue selected', async () => {
    renderCollectiveOffersSearchFilters({
      ...baseProps,
      selectedFilters: selectedVenueFilters,
    })

    const venueSelect = await screen.findByDisplayValue(
      expectedVenueSelectOptions[1].value
    )
    expect(venueSelect).toBeInTheDocument()
  })

  it('should display "Localisation" and "Toutes" when feature flag WIP_ENABLE_NEW_COLLECTIVE_OFFERS_AND_BOOKINGS_STRUCTURE is active', async () => {
    vi.mocked(useActiveFeature).mockReturnValue(true)
    renderCollectiveOffersSearchFilters({ ...baseProps })

    expect(await screen.findByLabelText('Localisation')).toBeInTheDocument()
    expect(
      await screen.findByRole('option', { name: 'Toutes' })
    ).toBeInTheDocument()
  })
})
