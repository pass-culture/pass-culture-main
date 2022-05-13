import {
  SAVE_PAGE_NUMBER,
  SAVE_SEARCH_FILTERS,
  SET_CATEGORIES,
} from './actions'

export const initialState = {
  list: [],
  searchFilters: {},
  pageNumber: 1,
  categories: {},
}

export const offersReducer = (state = initialState, action) => {
  switch (action.type) {
    case SAVE_SEARCH_FILTERS:
      return {
        ...state,
        searchFilters: { ...state.searchFilters, ...action.filters },
      }

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
