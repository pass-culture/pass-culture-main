import type { ListOffersQueryModel } from '@/apiClient/v1/new'
import { DEFAULT_SEARCH_FILTERS } from '@/commons/core/Offers/constants'
import { stringify } from '@/commons/utils/query-string'
import { translateApiParamsToQueryParams } from '@/commons/utils/translate'

import { Audience } from '../../shared/types'
import type { SearchListParams } from '../types'

const INDIVIDUAL_OFFERS_URL = '/offres'

export const computeIndividualOffersUrl = (
  offersSearchFilters: Partial<ListOffersQueryModel & SearchListParams>
): string => {
  const newFilters: Partial<ListOffersQueryModel & SearchListParams> =
    Object.entries({ page: 1, ...offersSearchFilters }).reduce(
      (accumulator, [filter, filterValue]) => {
        const defaultValue =
          DEFAULT_SEARCH_FILTERS[
            filter as keyof (ListOffersQueryModel & SearchListParams)
          ]
        if (filterValue === defaultValue || filterValue === undefined) {
          return accumulator
        }
        return Object.assign(accumulator, { [filter]: filterValue })
      },
      {} as Partial<ListOffersQueryModel & SearchListParams>
    )

  const queryString = stringify(
    translateApiParamsToQueryParams(newFilters, Audience.INDIVIDUAL)
  )
  return queryString
    ? `${INDIVIDUAL_OFFERS_URL}?${queryString}`
    : INDIVIDUAL_OFFERS_URL
}
