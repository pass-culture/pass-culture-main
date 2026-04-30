import type { ListOffersQueryModel } from '@/apiClient/v1/new'
import { DEFAULT_SEARCH_FILTERS } from '@/commons/core/Offers/constants'
import type { SearchListParams } from '@/commons/core/Offers/types'

// TODO (igabriele, 2025-11-07): This util seems redundant with `serializeApiIndividualFilters`. Consider merging the logic.
export function computeIndividualApiFilters(
  finalSearchFilters: Partial<ListOffersQueryModel & SearchListParams>,
  selectedOffererId: number
): ListOffersQueryModel & SearchListParams {
  const apiFilters: ListOffersQueryModel & SearchListParams = {
    ...DEFAULT_SEARCH_FILTERS,
    ...finalSearchFilters,
    offererId: selectedOffererId,
  }

  delete apiFilters.page
  return apiFilters
}
