import { DEFAULT_SEARCH_FILTERS } from '../constants'
import { TSearchFilters } from '../types'

export const hasSearchFilters = (
  searchFilters: TSearchFilters,
  filterNames: (keyof TSearchFilters)[] = Object.keys(
    searchFilters
  ) as (keyof TSearchFilters)[]
): boolean => {
  return filterNames
    .map(
      filterName =>
        searchFilters[filterName] !== { ...DEFAULT_SEARCH_FILTERS }[filterName]
    )
    .includes(true)
}
