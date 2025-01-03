import {
  ALL_STATUS,
  DEFAULT_SEARCH_FILTERS,
} from 'commons/core/Offers/constants'
import { SearchFiltersParams } from 'commons/core/Offers/types'
import { getStoredFilterConfig } from 'components/OffersTable/OffersTableSearch/utils'

export function computeIndividualApiFilters(
  urlSearchFilters: Partial<SearchFiltersParams>,
  selectedOffererId?: string | null,
  isRestrictedAsAdmin?: boolean
): SearchFiltersParams {
  const apiFilters: SearchFiltersParams = {
    ...DEFAULT_SEARCH_FILTERS,
    ...(getStoredFilterConfig('individual').storedFilters as SearchFiltersParams),
    ...urlSearchFilters,
    ...(isRestrictedAsAdmin ? { status: ALL_STATUS } : {}),
    ...{ offererId: selectedOffererId?.toString() ?? '' },
  }
  delete apiFilters.page
  return apiFilters
}
