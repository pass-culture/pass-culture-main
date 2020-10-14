export const SAVE_SEARCH_FILTERS = 'SAVE_SEARCH_FILTERS'
export const SET_SELECTED_OFFER_IDS = 'SET_SELECTED_OFFER_IDS'

export const initialState = {
  searchFilters: {},
  selectedOfferIds: [],
}

const offersReducers = (state = initialState, action) => {
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
    default:
      return state
  }
}

export function saveSearchFilters(filters) {
  return {
    filters,
    type: SAVE_SEARCH_FILTERS,
  }
}
export function setSelectedOfferIds(offerIds) {
  return {
    offerIds,
    type: SET_SELECTED_OFFER_IDS,
  }
}

export default offersReducers
