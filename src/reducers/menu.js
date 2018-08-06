const TOGGLE_MAIN_MENU = 'TOGGLE_MAIN_MENU'

export const toggleMainMenu = () => ({
  type: TOGGLE_MAIN_MENU,
})

export const menu = (state = false, action) => {
  switch (action.type) {
    case TOGGLE_MAIN_MENU:
      return !state
    default:
      return state
  }
}
