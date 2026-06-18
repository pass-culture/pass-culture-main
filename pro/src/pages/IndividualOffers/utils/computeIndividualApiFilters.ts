import type { ListOffersQueryModel } from '@/apiClient/v1'
import { DEFAULT_SEARCH_FILTERS } from '@/commons/core/Offers/constants'

import type { IndividualOffersFilters } from '../common/types'

type ComputeIndividualApiFiltersParams = {
  finalSearchFilters: Partial<IndividualOffersFilters>
  selectedVenueId: number
}

export function computeIndividualApiFilters(
  params: ComputeIndividualApiFiltersParams
): ListOffersQueryModel {
  const { finalSearchFilters, selectedVenueId } = params

  const { page: _, ...apiFilters } = {
    ...DEFAULT_SEARCH_FILTERS,
    ...finalSearchFilters,
    venueId: selectedVenueId,
  }

  return apiFilters
}
