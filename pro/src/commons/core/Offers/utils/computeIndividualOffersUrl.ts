import { DEFAULT_SEARCH_FILTERS } from '@/commons/core/Offers/constants'
import { stringify } from '@/commons/utils/query-string'
import { translateApiParamsToQueryParams } from '@/commons/utils/translate'

import { Audience } from '../../shared/types'
import { SearchFiltersParams } from '../types'

const INDIVIDUAL_OFFERS_URL = '/offres'

export const computeIndividualOffersUrl = (
  offersSearchFilters: Partial<SearchFiltersParams>
): string => {
  const emptyNewFilters: Partial<SearchFiltersParams> = {}
  const newFilters: Partial<SearchFiltersParams> = Object.entries({
    page: 1,
    ...offersSearchFilters,
  }).reduce((accumulator, [filter, filterValue]) => {
    if (
      filterValue !==
      DEFAULT_SEARCH_FILTERS[filter as keyof SearchFiltersParams]
    ) {
      return {
        ...accumulator,
        [filter]: filterValue,
      }
    }
    return accumulator
  }, emptyNewFilters)

  const queryString = stringify(
    translateApiParamsToQueryParams(newFilters, Audience.INDIVIDUAL)
  )
  return queryString
    ? `${INDIVIDUAL_OFFERS_URL}?${queryString}`
    : INDIVIDUAL_OFFERS_URL
}
