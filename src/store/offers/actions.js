export const SAVE_SEARCH_FILTERS = 'SAVE_SEARCH_FILTERS'
export const SET_OFFERS = 'SET_OFFERS'

export const saveSearchFilters = filters => ({
  filters,
  type: SAVE_SEARCH_FILTERS,
})

export const setOffers = offers => ({
  offers,
  type: SET_OFFERS,
})
