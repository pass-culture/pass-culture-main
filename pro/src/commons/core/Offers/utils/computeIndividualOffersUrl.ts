import { DEFAULT_SEARCH_FILTERS } from '@/commons/core/Offers/constants'
import { stringify } from '@/commons/utils/query-string'
import { translateApiParamsToQueryParams } from '@/commons/utils/translate'

import { Audience } from '../../shared/types'
import type { IndividualSearchFiltersParams } from '../types'

const INDIVIDUAL_OFFERS_URL = '/offres'

export const computeIndividualOffersUrl = (
  offersSearchFilters: Partial<IndividualSearchFiltersParams>
): string => {
  const emptyNewFilters: Partial<IndividualSearchFiltersParams> = {}
  const newFilters: Partial<IndividualSearchFiltersParams> = Object.entries({
    page: 1,
    ...offersSearchFilters,
  }).reduce(
    (accumulator, [filter, filterValue]) =>
      filterValue ===
      DEFAULT_SEARCH_FILTERS[filter as keyof IndividualSearchFiltersParams]
        ? accumulator
        : Object.assign(accumulator, {
            [filter]: filterValue,
          }),
    emptyNewFilters
  )

  const queryString = stringify(
    translateApiParamsToQueryParams(newFilters, Audience.INDIVIDUAL)
  )
  return queryString
    ? `${INDIVIDUAL_OFFERS_URL}?${queryString}`
    : INDIVIDUAL_OFFERS_URL
}
