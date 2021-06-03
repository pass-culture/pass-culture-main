import { SAVE_SEARCH_FILTERS, SET_OFFERS } from './actions'

export const initialState = {
  list: [],
  searchFilters: {},
}

export const offersReducer = (state = initialState, action) => {
  switch (action.type) {
    case SAVE_SEARCH_FILTERS: {
      return { ...state, searchFilters: { ...state.searchFilters, ...action.filters } }
    }
    case SET_OFFERS:
      return { ...state, list: action.offers }
    default:
      return state
  }
}
