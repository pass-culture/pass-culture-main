const TOGGLE_FILTER_MENU = 'TOGGLE_FILTER_MENU'

export const toggleFilterMenu = () => ({
  type: TOGGLE_FILTER_MENU,
})

export const menu = (state = false, action) => {
  switch (action.type) {
    case TOGGLE_FILTER_MENU:
      return !state
    default:
      return state
  }
}
