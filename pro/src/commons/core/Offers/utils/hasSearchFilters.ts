import { DEFAULT_SEARCH_FILTERS } from '../constants'
import { CollectiveSearchFiltersParams, SearchFiltersParams } from '../types'

type HasSearchFiltersParams = {
  searchFilters: Partial<SearchFiltersParams>
  lookup?: (keyof SearchFiltersParams)[]
  ignore?: (keyof SearchFiltersParams)[]
}
export const hasSearchFilters = ({
  searchFilters,
  lookup = Object.keys(searchFilters) as (keyof SearchFiltersParams)[],
  ignore = [],
}: HasSearchFiltersParams): boolean => {
  // Those "filters" are ignored because none are to be interpreted
  // as such by the user.
  const finalIgnore = ['offererId', 'page', ...ignore]

  return lookup.some(
    (filterName) =>
      searchFilters[filterName] &&
      searchFilters[filterName] !== { ...DEFAULT_SEARCH_FILTERS }[filterName] &&
      !finalIgnore.includes(filterName)
  )
}

type HasCollectiveSearchFiltersParams = {
  searchFilters: Partial<CollectiveSearchFiltersParams>
  defaultFilters: CollectiveSearchFiltersParams
  lookup?: (keyof CollectiveSearchFiltersParams)[]
  ignore?: (keyof CollectiveSearchFiltersParams)[]
}
export const hasCollectiveSearchFilters = ({
  searchFilters,
  defaultFilters,
  lookup = Object.keys(
    searchFilters
  ) as (keyof CollectiveSearchFiltersParams)[],
  ignore = [],
}: HasCollectiveSearchFiltersParams): boolean => {
  // Those "filters" are ignored because none are to be interpreted
  // as such by the user.
  const finalIgnore = ['offererId', 'page', ...ignore]

  return lookup.some(
    (filterName) =>
      searchFilters[filterName] &&
      ((['string', 'number'].includes(typeof searchFilters[filterName]) &&
        searchFilters[filterName] !== { ...defaultFilters }[filterName]) ||
        (Array.isArray(searchFilters[filterName]) &&
          Array.isArray(defaultFilters[filterName]) &&
          !isSameArray(
            searchFilters[filterName],
            defaultFilters[filterName]
          ))) &&
      !finalIgnore.includes(filterName)
  )
}

function isSameArray(arr1: unknown[], arr2: unknown[]) {
  return arr1.length === arr2.length && arr1.every((el) => arr2.includes(el))
}
