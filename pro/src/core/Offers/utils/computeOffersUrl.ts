import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { stringify } from 'utils/query-string'
import { translateApiParamsToQueryParams } from 'utils/translate'

import { Audience } from '../../shared/types'
import { SearchFiltersParams } from '../types'

const INDIVIDUAL_OFFERS_URL = '/offres'
const COLLECTIVE_OFFERS_URL = '/offres/collectives'

const computeOffersUrlForGivenAudience = (
  audience: Audience,
  offersSearchFilters: Partial<SearchFiltersParams>
): string => {
  const emptyNewFilters: Partial<SearchFiltersParams> = {}
  const newFilters: Partial<SearchFiltersParams> = Object.entries(
    offersSearchFilters
  ).reduce((accumulator, [filter, filterValue]) => {
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

  if (audience === Audience.COLLECTIVE) {
    const queryString = Object.entries(
      translateApiParamsToQueryParams(newFilters, audience)
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

  const queryString = stringify(
    translateApiParamsToQueryParams(newFilters, audience)
  )
  return queryString
    ? `${INDIVIDUAL_OFFERS_URL}?${queryString}`
    : INDIVIDUAL_OFFERS_URL
}

export const computeOffersUrl = (
  offersSearchFilters: Partial<SearchFiltersParams>
): string =>
  computeOffersUrlForGivenAudience(Audience.INDIVIDUAL, {
    page: 1,
    ...offersSearchFilters,
  })

export const computeCollectiveOffersUrl = (
  offersSearchFilters: Partial<SearchFiltersParams> & { page?: number }
): string =>
  computeOffersUrlForGivenAudience(Audience.COLLECTIVE, {
    page: 1,
    ...offersSearchFilters,
  })
