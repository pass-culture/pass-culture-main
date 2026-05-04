import { DEFAULT_SEARCH_FILTERS } from '@/commons/core/Offers/constants'
import { stringify } from '@/commons/utils/query-string'
import { translateApiParamsToQueryParams } from '@/commons/utils/translate'
import type { IndividualOffersFilters } from '@/pages/IndividualOffers/common/types'

import { Audience } from '../../shared/types'

const INDIVIDUAL_OFFERS_URL = '/offres'

export const computeIndividualOffersUrl = (
  offersSearchFilters: Partial<IndividualOffersFilters>
): string => {
  const newFilters: Partial<IndividualOffersFilters> = Object.entries({
    page: 1,
    ...offersSearchFilters,
  }).reduce(
    (accumulator, [filter, filterValue]) => {
      const defaultValue =
        DEFAULT_SEARCH_FILTERS[filter as keyof IndividualOffersFilters]
      if (filterValue === defaultValue || filterValue === undefined) {
        return accumulator
      }
      return Object.assign(accumulator, { [filter]: filterValue })
    },
    {} as Partial<IndividualOffersFilters>
  )

  const queryString = stringify(
    translateApiParamsToQueryParams(newFilters, Audience.INDIVIDUAL)
  )
  return queryString
    ? `${INDIVIDUAL_OFFERS_URL}?${queryString}`
    : INDIVIDUAL_OFFERS_URL
}
