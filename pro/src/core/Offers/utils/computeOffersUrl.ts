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
  const newFilters = Object.entries(offersSearchFilters).reduce(
    (accumulator, [filter, filterValue]) => {
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
    },
    emptyNewFilters
  )

  const queryString = stringify(translateApiParamsToQueryParams(newFilters))
  const baseUrl =
    audience === Audience.INDIVIDUAL
      ? INDIVIDUAL_OFFERS_URL
      : COLLECTIVE_OFFERS_URL
  return queryString ? `${baseUrl}?${queryString}` : baseUrl
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
