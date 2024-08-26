import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { translateApiParamsToQueryParams } from 'utils/translate'

import { Audience } from '../../shared/types'
import { CollectiveSearchFiltersParams } from '../types'

const COLLECTIVE_OFFERS_URL = '/offres/collectives'

export const computeCollectiveOffersUrl = (
  offersSearchFilters: Partial<CollectiveSearchFiltersParams>
): string => {
  const emptyNewFilters: Partial<CollectiveSearchFiltersParams> = {}
  const newFilters: Partial<CollectiveSearchFiltersParams> = Object.entries({
    page: 1,
    ...offersSearchFilters,
  }).reduce((accumulator, [filter, filterValue]) => {
    if (
      filterValue !==
      DEFAULT_SEARCH_FILTERS[filter as keyof CollectiveSearchFiltersParams]
    ) {
      return {
        ...accumulator,
        [filter]: filterValue,
      }
    }
    return accumulator
  }, emptyNewFilters)

  const queryString = Object.entries(
    translateApiParamsToQueryParams(newFilters, Audience.COLLECTIVE)
  )
    .flatMap(([key, value]) =>
      Array.isArray(value)
        ? value.map((v) => `${key}=${encodeURIComponent(v)}`)
        : `${key}=${encodeURIComponent(value as string)}`
    )
    .join('&')

  return queryString
    ? `${COLLECTIVE_OFFERS_URL}?${queryString}`
    : COLLECTIVE_OFFERS_URL
}
