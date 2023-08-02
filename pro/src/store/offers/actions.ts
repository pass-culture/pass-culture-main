import { SearchFiltersParams } from 'core/Offers/types'

export const SAVE_SEARCH_FILTERS = 'SAVE_SEARCH_FILTERS'
export const SAVE_PAGE_NUMBER = 'SAVE_PAGE_NUMBER'

export interface SaveSearchFiltersAction {
  type: typeof SAVE_SEARCH_FILTERS
  filters: Partial<SearchFiltersParams>
}

export const saveSearchFilters = (
  filters: Partial<SearchFiltersParams>
): SaveSearchFiltersAction => ({
  filters,
  type: SAVE_SEARCH_FILTERS,
})

export interface SavePageNumberAction {
  type: typeof SAVE_PAGE_NUMBER
  pageNumber: number
}

export const savePageNumber = (pageNumber: number): SavePageNumberAction => ({
  pageNumber,
  type: SAVE_PAGE_NUMBER,
})
