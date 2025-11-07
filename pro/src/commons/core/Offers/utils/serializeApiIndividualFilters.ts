import type { ListOffersQueryModel } from '@/apiClient/v1'

import { DEFAULT_SEARCH_FILTERS } from '../constants'
import type { IndividualSearchFiltersParams } from '../types'

// TODO (igabriele, 2025-11-07): This function is overly complicated for what it does and its typing is unreliable.
export const serializeApiIndividualFilters = (
  searchFilters: Partial<IndividualSearchFiltersParams>
): Omit<ListOffersQueryModel, 'collectiveOfferType'> => {
  const listOffersQueryKeys: (keyof Omit<
    ListOffersQueryModel,
    'collectiveOfferType'
  >)[] = [
    'nameOrIsbn',
    'offererId',
    'status',
    'venueId',
    'offererAddressId',
    'categoryId',
    'creationMode',
    'periodBeginningDate',
    'periodEndingDate',
  ]

  const body: Omit<ListOffersQueryModel, 'collectiveOfferType'> = {}
  const defaultFilters = DEFAULT_SEARCH_FILTERS
  return listOffersQueryKeys.reduce((accumulator, field) => {
    const filterValue = searchFilters[field]
    if (filterValue && filterValue !== defaultFilters[field]) {
      ;(accumulator as any)[field] = filterValue
    }
    return accumulator
  }, body)
}
