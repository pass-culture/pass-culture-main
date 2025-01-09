import {
  ALL_STATUS,
  DEFAULT_SEARCH_FILTERS,
} from 'commons/core/Offers/constants'
import { SearchFiltersParams } from 'commons/core/Offers/types'

export function computeIndividualApiFilters(
  finalSearchFilters: Partial<SearchFiltersParams>,
  selectedOffererId?: string | null,
  isRestrictedAsAdmin?: boolean,
): SearchFiltersParams {
  const apiFilters: SearchFiltersParams = {
    ...DEFAULT_SEARCH_FILTERS,
    ...finalSearchFilters,
    ...(isRestrictedAsAdmin ? { status: ALL_STATUS } : {}),
    ...{ offererId: selectedOffererId?.toString() ?? '' },
  }

  delete apiFilters.page
  return apiFilters
}
