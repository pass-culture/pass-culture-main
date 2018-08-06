const TOGGLE_MAIN_MENU = 'TOGGLE_MAIN_MENU'
const LOCATION_CHANGE = '@@router/LOCATION_CHANGE'

export const toggleMainMenu = () => ({
  type: TOGGLE_MAIN_MENU,
})

export const menu = (state = false, action) => {
  switch (action.type) {
    case TOGGLE_MAIN_MENU:
      return !state
    case LOCATION_CHANGE:
      return false
    default:
      return state
  }
}
