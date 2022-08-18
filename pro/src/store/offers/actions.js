export const SAVE_SEARCH_FILTERS = 'SAVE_SEARCH_FILTERS'
export const SAVE_PAGE_NUMBER = 'SAVE_PAGE_NUMBER'
export const SET_CATEGORIES = 'SET_CATEGORIES'

export const saveSearchFilters = filters => ({
  filters,
  type: SAVE_SEARCH_FILTERS,
})

export const savePageNumber = pageNumber => ({
  pageNumber,
  type: SAVE_PAGE_NUMBER,
})
