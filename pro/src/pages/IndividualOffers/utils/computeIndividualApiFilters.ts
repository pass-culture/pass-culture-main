import type { ListOffersQueryModel } from '@/apiClient/v1/new'
import { DEFAULT_SEARCH_FILTERS } from '@/commons/core/Offers/constants'

import type { IndividualOffersFilters } from '../common/types'

export function computeIndividualApiFilters(
  finalSearchFilters: Partial<IndividualOffersFilters>,
  selectedVenueId: number
): ListOffersQueryModel {
  const { page: _, ...apiFilters } = {
    ...DEFAULT_SEARCH_FILTERS,
    ...finalSearchFilters,
    venueId: selectedVenueId,
  }

  return apiFilters
}
