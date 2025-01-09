import { DEFAULT_SEARCH_FILTERS } from '../constants'
import { CollectiveSearchFiltersParams, SearchFiltersParams } from '../types'

export const hasSearchFilters = (
  searchFilters: Partial<SearchFiltersParams>,
  filterNames: (keyof SearchFiltersParams)[] = Object.keys(
    searchFilters
  ) as (keyof SearchFiltersParams)[]
): boolean => {
  return filterNames.some(
    (filterName) =>
      searchFilters[filterName] &&
      filterName !== 'offererId' &&
      filterName !== 'page' &&
      searchFilters[filterName] !== { ...DEFAULT_SEARCH_FILTERS }[filterName]
  )
}

export const hasCollectiveSearchFilters = (
  searchFilters: Partial<CollectiveSearchFiltersParams>,
  defaultFilters: CollectiveSearchFiltersParams,
  filterNames: (keyof CollectiveSearchFiltersParams)[] = Object.keys(
    searchFilters
  ) as (keyof CollectiveSearchFiltersParams)[]
): boolean => {
  return filterNames.some(
    (filterName) =>
      searchFilters[filterName] &&
      filterName !== 'offererId' &&
      filterName !== 'page' &&
      searchFilters[filterName] !== { ...defaultFilters }[filterName]
  )
}
