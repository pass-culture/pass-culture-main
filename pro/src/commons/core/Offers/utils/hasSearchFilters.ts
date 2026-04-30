import type { ListOffersQueryModel } from '@/apiClient/v1/new'

import { DEFAULT_SEARCH_FILTERS } from '../constants'
import type { CollectiveSearchFiltersParams, SearchListParams } from '../types'

type IndividualFilterShape = ListOffersQueryModel & SearchListParams

type HasSearchFiltersParams = {
  searchFilters: Partial<IndividualFilterShape>
  lookup?: (keyof IndividualFilterShape)[]
  ignore?: (keyof IndividualFilterShape)[]
}
export const hasSearchFilters = ({
  searchFilters,
  lookup = Object.keys(searchFilters) as (keyof IndividualFilterShape)[],
  ignore = [],
}: HasSearchFiltersParams): boolean => {
  // Those "filters" are ignored because none are to be interpreted
  // as such by the user.
  const finalIgnore = new Set(['offererId', 'page', ...ignore])

  return lookup.some(
    (filterName) =>
      searchFilters[filterName] !== undefined &&
      searchFilters[filterName] !== { ...DEFAULT_SEARCH_FILTERS }[filterName] &&
      !finalIgnore.has(filterName)
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
  const finalIgnore = new Set(['offererId', 'page', ...ignore])

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
      !finalIgnore.has(filterName)
  )
}

function isSameArray(arr1: unknown[], arr2: unknown[]) {
  return arr1.length === arr2.length && arr1.every((el) => arr2.includes(el))
}
