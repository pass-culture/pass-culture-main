import { SAVE_SEARCH_FILTERS, SET_OFFERS, SET_CATEGORIES, SAVE_PAGE_NUMBER } from './actions'

export const initialState = {
  list: [],
  searchFilters: {},
  pageNumber: 1,
  categories: {},
}

export const offersReducer = (state = initialState, action) => {
  switch (action.type) {
    case SAVE_SEARCH_FILTERS:
      return { ...state, searchFilters: { ...state.searchFilters, ...action.filters } }

    case SET_OFFERS:
      return { ...state, list: action.offers }

    case SAVE_PAGE_NUMBER:
      return { ...state, pageNumber: action.pageNumber }

    case SET_CATEGORIES:
      return {
        ...state,
        categories: action.categories,
      }

    default:
      return state
  }
}
