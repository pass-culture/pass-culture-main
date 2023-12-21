import { SearchFiltersParams } from 'core/Offers/types'
import { RootState } from 'store/reducers'

export const searchFiltersSelector = (
  state: RootState
): Partial<SearchFiltersParams> => state.offers.searchFilters
