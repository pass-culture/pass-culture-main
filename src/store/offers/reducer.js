import { SAVE_SEARCH_FILTERS, SET_OFFERS } from './actions'

export const initialState = {
  list: [],
  searchFilters: {},
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
    case SET_OFFERS:
      return { ...state, list: action.offers }
    default:
      return state
  }
}
