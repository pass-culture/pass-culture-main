import type { ListOffersQueryModel } from '@/apiClient/v1'

import { DEFAULT_SEARCH_FILTERS } from '../constants'
import type { SearchFiltersParams } from '../types'

export const serializeApiFilters = (
  searchFilters: Partial<SearchFiltersParams>
): ListOffersQueryModel => {
  const listOffersQueryKeys: (keyof ListOffersQueryModel)[] = [
    'nameOrIsbn',
    'offererId',
    'status',
    'venueId',
    'offererAddressId',
    'categoryId',
    'creationMode',
    'periodBeginningDate',
    'periodEndingDate',
    'collectiveOfferType',
  ]

  const body: ListOffersQueryModel = {}
  const defaultFilters = DEFAULT_SEARCH_FILTERS
  return listOffersQueryKeys.reduce((accumulator, field) => {
    const filterValue = searchFilters[field]
    if (filterValue && filterValue !== defaultFilters[field]) {
      ;(accumulator as any)[field] = filterValue
    }
    return accumulator
  }, body)
}
