import {
  ListCollectiveOffersQueryModel,
  ListOffersQueryModel,
} from 'apiClient/v1'

import { DEFAULT_SEARCH_FILTERS } from '../constants'
import { SearchFiltersParams } from '../types'

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
    'offererAddressId',
  ]

  const body: ListOffersQueryModel & ListCollectiveOffersQueryModel = {}
  return listOffersQueryKeys.reduce((accumulator, field) => {
    const filterValue = searchFilters[field]
    if (filterValue && filterValue !== DEFAULT_SEARCH_FILTERS[field]) {
      return {
        ...accumulator,
        [field]: filterValue,
      }
    }
    return accumulator
  }, body)
}
