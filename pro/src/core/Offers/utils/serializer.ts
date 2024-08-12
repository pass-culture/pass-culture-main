import {
  ListCollectiveOffersQueryModel,
  ListOffersQueryModel,
} from 'apiClient/v1'
import { Audience } from 'core/shared/types'

import {
  DEFAULT_COLLECTIVE_SEARCH_FILTERS,
  DEFAULT_SEARCH_FILTERS,
} from '../constants'
import { SearchFiltersParams } from '../types'

export const serializeApiFilters = (
  searchFilters: Partial<SearchFiltersParams>,
  audience: Audience
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
  const defaultFilters =
    audience === Audience.INDIVIDUAL
      ? DEFAULT_SEARCH_FILTERS
      : DEFAULT_COLLECTIVE_SEARCH_FILTERS
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
