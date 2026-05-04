import type { ListOffersQueryModel } from '@/apiClient/v1/new'
import { DEFAULT_SEARCH_FILTERS } from '@/commons/core/Offers/constants'

import type { IndividualOffersFilters } from '../common/types'

// TODO (igabriele, 2025-11-07): This util seems redundant with `serializeApiIndividualFilters`. Consider merging the logic.
export function computeIndividualApiFilters(
  finalSearchFilters: Partial<IndividualOffersFilters>,
  selectedOffererId: number
): ListOffersQueryModel {
  const { page: _, ...apiFilters } = {
    ...DEFAULT_SEARCH_FILTERS,
    ...finalSearchFilters,
    offererId: selectedOffererId,
  }

  return apiFilters
}
