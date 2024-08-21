import {
  ListCollectiveOffersQueryModel,
  ListOffersQueryModel,
} from 'apiClient/v1'

import {
  DEFAULT_COLLECTIVE_SEARCH_FILTERS,
  DEFAULT_SEARCH_FILTERS,
} from '../constants'
import { CollectiveSearchFiltersParams, SearchFiltersParams } from '../types'

export const serializeApiFilters = (
  searchFilters: Partial<SearchFiltersParams>
): ListOffersQueryModel & ListCollectiveOffersQueryModel => {
  const listOffersQueryKeys: (
    | keyof ListOffersQueryModel
    | keyof ListCollectiveOffersQueryModel
  )[] = [
    'nameOrIsbn',
    'offererId',
    'status',
    'venueId',
    'categoryId',
    'creationMode',
    'periodBeginningDate',
    'periodEndingDate',
    'collectiveOfferType',
    'format',
  ]

  const body: ListOffersQueryModel & ListCollectiveOffersQueryModel = {}
  const defaultFilters = DEFAULT_SEARCH_FILTERS
  return listOffersQueryKeys.reduce((accumulator, field) => {
    const filterValue = searchFilters[field]
    if (filterValue && filterValue !== defaultFilters[field]) {
      return {
        ...accumulator,
        [field]: filterValue,
      }
    }
    return accumulator
  }, body)
}

export const serializeApiCollectiveFilters = (
  searchFilters: Partial<CollectiveSearchFiltersParams>
): ListCollectiveOffersQueryModel => {
  const listOffersQueryKeys = [
    'nameOrIsbn',
    'offererId',
    'status',
    'venueId',
    'periodBeginningDate',
    'periodEndingDate',
    'collectiveOfferType',
    'format',
  ] satisfies (keyof CollectiveSearchFiltersParams)[]

  const body: ListOffersQueryModel & ListCollectiveOffersQueryModel = {}
  const defaultFilters = DEFAULT_COLLECTIVE_SEARCH_FILTERS
  return listOffersQueryKeys.reduce((accumulator, field) => {
    const filterValue = searchFilters[field]
    if (filterValue && filterValue !== defaultFilters[field]) {
      return {
        ...accumulator,
        [field]: filterValue,
      }
    }
    return accumulator
  }, body)
}
