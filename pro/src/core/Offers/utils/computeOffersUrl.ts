import {
  ALL_CREATION_MODES,
  ALL_STATUS,
  DEFAULT_PAGE,
  DEFAULT_SEARCH_FILTERS,
} from 'core/Offers/constants'
import { stringify } from 'utils/query-string'
import {
  mapApiToBrowser,
  translateApiParamsToQueryParams,
} from 'utils/translate'

import { Audience } from '../../shared/types'
import { SearchFiltersParams } from '../types'

const INDIVIDUAL_OFFERS_URL = '/offres'
const COLLECTIVE_OFFERS_URL = '/offres/collectives'

const computeOffersUrlForGivenAudience = (
  audience: Audience,
  offersSearchFilters: Partial<SearchFiltersParams> & { page?: number },
  offersPageNumber: number
): string => {
  const { creationMode, status } = offersSearchFilters
  const searchFiltersParams = { ...offersSearchFilters }
  if (status && status !== ALL_STATUS) {
    searchFiltersParams.status = mapApiToBrowser[status]
  }
  if (creationMode && creationMode !== ALL_CREATION_MODES) {
    searchFiltersParams.creationMode = mapApiToBrowser[creationMode]
  }

  if (offersPageNumber !== DEFAULT_PAGE) {
    searchFiltersParams.page = offersPageNumber
  }

  const keys = Object.keys(searchFiltersParams) as (keyof SearchFiltersParams)[]

  const newFilters: Partial<SearchFiltersParams> = {}
  keys.forEach(key => {
    if (searchFiltersParams[key] !== DEFAULT_SEARCH_FILTERS[key]) {
      // @ts-expect-error next FIX ME: newFilters['status'] is not string...
      newFilters[key] = searchFiltersParams[key]
    }
  })

  const queryString = stringify(translateApiParamsToQueryParams(newFilters))
  const baseUrl =
    audience === Audience.INDIVIDUAL
      ? INDIVIDUAL_OFFERS_URL
      : COLLECTIVE_OFFERS_URL
  return queryString ? `${baseUrl}?${queryString}` : baseUrl
}

export const computeOffersUrl = (
  offersSearchFilters: Partial<SearchFiltersParams> & { page?: number },
  offersPageNumber = 1
): string =>
  computeOffersUrlForGivenAudience(
    Audience.INDIVIDUAL,
    offersSearchFilters,
    offersPageNumber
  )

export const computeCollectiveOffersUrl = (
  offersSearchFilters: Partial<SearchFiltersParams> & { page?: number },
  offersPageNumber = 1
): string =>
  computeOffersUrlForGivenAudience(
    Audience.COLLECTIVE,
    offersSearchFilters,
    offersPageNumber
  )
