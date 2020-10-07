export const SAVE_SEARCH_FILTERS = 'SAVE_SEARCH_FILTERS'

const initialState = {
  searchFilters: {},
}

const offersReducers = (state = initialState, action) => {
  switch (action.type) {
    case SAVE_SEARCH_FILTERS:
      let filters = {}
      Object.keys(action.filters).forEach((filterName) => {
        if (action.filters[filterName]) {
          filters[filterName] = action.filters[filterName]
        }
      })
      return Object.assign({}, state, {
        searchFilters: filters,
      })
    default:
      return state
  }
}

export function saveSearchFilters(searchFilters) {
  return {
    searchFilters,
    type: SAVE_SEARCH_FILTERS,
  }
}

export default offersReducers
