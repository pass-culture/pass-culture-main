export const SAVE_SEARCH_FILTERS = 'SAVE_SEARCH_FILTERS'
export const SET_OFFERS = 'SET_OFFERS'
export const SAVE_PAGE_NUMBER = 'SAVE_PAGE_NUMBER'

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
