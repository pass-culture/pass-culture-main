import { screen } from '@testing-library/react'

import { DEFAULT_COLLECTIVE_SEARCH_FILTERS } from '@/commons/core/Offers/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
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
} from './CollectiveOffersSearchFilters'

vi.mock('@/apiClient/api', () => {
  return {
    api: {
      listOfferersNames: vi.fn().mockReturnValue({}),
      deleteDraftOffers: vi.fn(),
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
  offererId: '1',
  selectedFilters: DEFAULT_COLLECTIVE_SEARCH_FILTERS,
  setSelectedFilters: () => {},
  disableAllFilters: false,
  resetFilters: () => {},
}

describe('CollectiveOffersSearchFilters', () => {
  it('should display location filter', async () => {
    vi.mocked(useActiveFeature).mockReturnValue(true)
    renderCollectiveOffersSearchFilters({ ...baseProps })

    expect(await screen.findByLabelText('Localisation')).toBeInTheDocument()
    expect(
      await screen.findByRole('option', { name: 'Toutes' })
    ).toBeInTheDocument()
  })
})
