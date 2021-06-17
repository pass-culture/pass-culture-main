import { SAVE_PAGE_NUMBER, SAVE_SEARCH_FILTERS, SET_OFFERS } from './actions'

export const initialState = {
  list: [],
  searchFilters: {},
  pageNumber: 1,
}

export const offersReducer = (state = initialState, action) => {
  switch (action.type) {
    case SAVE_SEARCH_FILTERS: {
      return { ...state, searchFilters: { ...state.searchFilters, ...action.filters } }
    }
    case SET_OFFERS:
      return { ...state, list: action.offers }
    case SAVE_PAGE_NUMBER: {
      return { ...state, pageNumber: action.pageNumber }
    }
    default:
      return state
  }
}
