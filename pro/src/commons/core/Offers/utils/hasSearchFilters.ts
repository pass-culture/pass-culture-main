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
      ((['string', 'number'].includes(typeof searchFilters[filterName]) &&
        searchFilters[filterName] !== { ...defaultFilters }[filterName]) ||
        (Array.isArray(searchFilters[filterName]) &&
          Array.isArray(defaultFilters[filterName]) &&
          !isSameArray(searchFilters[filterName], defaultFilters[filterName])))
  )
}

function isSameArray(arr1: unknown[], arr2: unknown[]) {
  return arr1.length === arr2.length && arr1.every((el) => arr2.includes(el))
}
