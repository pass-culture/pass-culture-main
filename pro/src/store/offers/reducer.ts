import {
  SAVE_PAGE_NUMBER,
  SAVE_SEARCH_FILTERS,
  SavePageNumberAction,
  SaveSearchFiltersAction,
} from './actions'

const initialState = {
  list: [],
  searchFilters: {},
  pageNumber: 1,
  categories: {},
}

export const offersReducer = (
  state = initialState,
  action: SaveSearchFiltersAction | SavePageNumberAction
) => {
  switch (action.type) {
    case SAVE_SEARCH_FILTERS:
      return {
        ...state,
        searchFilters: { ...state.searchFilters, ...action.filters },
      }

    case SAVE_PAGE_NUMBER:
      return { ...state, pageNumber: action.pageNumber }

    default:
      return state
  }
}
