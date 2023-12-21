import { DEFAULT_SEARCH_FILTERS } from '../constants'
import { SearchFiltersParams } from '../types'

export const hasSearchFilters = (
  searchFilters: Partial<SearchFiltersParams>,
  filterNames: (keyof SearchFiltersParams)[] = Object.keys(
    searchFilters
  ) as (keyof SearchFiltersParams)[]
): boolean => {
  return filterNames
    .map(
      (filterName) =>
        searchFilters[filterName] !== { ...DEFAULT_SEARCH_FILTERS }[filterName]
    )
    .includes(true)
}
