import { TSearchFilters } from 'core/Offers/types'

export const searchFiltersSelector = (state: any): TSearchFilters =>
  state.offers.searchFilters
