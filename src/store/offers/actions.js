export const SAVE_SEARCH_FILTERS = 'SAVE_SEARCH_FILTERS'
export const SET_SELECTED_OFFER_IDS = 'SET_SELECTED_OFFER_IDS'
export const SET_OFFERS = 'SET_OFFERS'

export const saveSearchFilters = filters => ({
  filters,
  type: SAVE_SEARCH_FILTERS,
})

export const setSelectedOfferIds = offerIds => ({
  offerIds,
  type: SET_SELECTED_OFFER_IDS,
})

export const setOffers = offers => ({
  offers,
  type: SET_OFFERS,
})
