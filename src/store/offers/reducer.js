import { SAVE_SEARCH_FILTERS, SET_OFFERS, SET_SELECTED_OFFER_IDS } from './actions'

export const initialState = {
  list: [],
  searchFilters: {},
  selectedOfferIds: [],
}

export const offersReducer = (state = initialState, action) => {
  switch (action.type) {
    case SAVE_SEARCH_FILTERS: {
      let filters = {}
      Object.keys(action.filters).forEach(filterName => {
        if (action.filters[filterName]) {
          filters[filterName] = action.filters[filterName]
        }
      })
      return { ...state, searchFilters: filters }
    }
    case SET_SELECTED_OFFER_IDS:
      return { ...state, selectedOfferIds: action.offerIds }
    case SET_OFFERS:
      return { ...state, list: action.offers }
    default:
      return state
  }
}
