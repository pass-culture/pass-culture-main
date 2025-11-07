import { DEFAULT_SEARCH_FILTERS } from '@/commons/core/Offers/constants'
import type { IndividualSearchFiltersParams } from '@/commons/core/Offers/types'

// TODO (igabriele, 2025-11-07): This util seems redundant with `serializeApiIndividualFilters`. Consider merging the logic.
export function computeIndividualApiFilters(
  finalSearchFilters: Partial<IndividualSearchFiltersParams>,
  selectedOffererId?: string | null
): IndividualSearchFiltersParams {
  const apiFilters: IndividualSearchFiltersParams = {
    ...DEFAULT_SEARCH_FILTERS,
    ...finalSearchFilters,
    ...{ offererId: selectedOffererId?.toString() ?? '' },
  }

  delete apiFilters.page
  return apiFilters
}
