import {
  ALL_STATUS,
  DEFAULT_SEARCH_FILTERS,
} from 'commons/core/Offers/constants'
import { SearchFiltersParams } from 'commons/core/Offers/types'
import { localStorageAvailable } from 'commons/utils/localStorageAvailable'

export function computeIndividualApiFilters(
  urlSearchFilters: SearchFiltersParams,
  selectedOffererId?: string | null,
  isRestrictedAsAdmin?: boolean
): SearchFiltersParams {
  const isLocalStorageAvailable = localStorageAvailable()
  const apiFilters: SearchFiltersParams = {
    ...DEFAULT_SEARCH_FILTERS,
    ...urlSearchFilters,
    ...(isRestrictedAsAdmin ? { status: ALL_STATUS } : {}),
    ...{ offererId: selectedOffererId?.toString() ?? '' },
    ...(isLocalStorageAvailable ? 
      JSON.parse(localStorage.getItem('INDIVIDUAL_OFFERS_FILTER_CONFIG') ?? '{}') :
      {}
    )
  }
  delete apiFilters.page
  return apiFilters
}
