import { translateApiParamsToQueryParams } from '@/commons/utils/translate'

import { Audience } from '../../shared/types'
import { DEFAULT_COLLECTIVE_SEARCH_FILTERS } from '../constants'
import { CollectiveSearchFiltersParams } from '../types'

const COLLECTIVE_OFFERS_URL = '/offres/collectives'
const TEMPLATE_COLLECTIVE_OFFERS_URL = '/offres/vitrines'

export const computeCollectiveOffersUrl = (
  offersSearchFilters: Partial<CollectiveSearchFiltersParams>,
  defaultFilters: CollectiveSearchFiltersParams = DEFAULT_COLLECTIVE_SEARCH_FILTERS,
  shouldComputeTemplateOfferUrl?: boolean
): string => {
  const emptyNewFilters: Partial<CollectiveSearchFiltersParams> = {}
  const newFilters: Partial<CollectiveSearchFiltersParams> = Object.entries({
    page: 1,
    ...offersSearchFilters,
  }).reduce((accumulator, [filter, filterValue]) => {
    if (
      filterValue !==
      defaultFilters[filter as keyof CollectiveSearchFiltersParams]
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

  const url = shouldComputeTemplateOfferUrl
    ? TEMPLATE_COLLECTIVE_OFFERS_URL
    : COLLECTIVE_OFFERS_URL

  return queryString ? `${url}?${queryString}` : url
}
