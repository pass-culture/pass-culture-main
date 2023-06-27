import { SearchFiltersParams } from 'core/Offers/types'

export const searchFiltersSelector = (state: any): SearchFiltersParams =>
  state.offers.searchFilters
