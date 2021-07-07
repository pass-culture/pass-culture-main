export const SAVE_SEARCH_FILTERS = 'SAVE_SEARCH_FILTERS'
export const SET_OFFERS = 'SET_OFFERS'
export const SAVE_PAGE_NUMBER = 'SAVE_PAGE_NUMBER'
export const SET_CATEGORIES = 'SET_CATEGORIES'

export const saveSearchFilters = filters => ({
  filters,
  type: SAVE_SEARCH_FILTERS,
})

export const setOffers = offers => ({
  offers,
  type: SET_OFFERS,
})

export const savePageNumber = pageNumber => ({
  pageNumber,
  type: SAVE_PAGE_NUMBER,
})

export const setCategories = categories => ({
  categories,
  type: SET_CATEGORIES,
})
