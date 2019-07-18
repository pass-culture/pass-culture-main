const TOGGLE_MAIN_MENU = 'TOGGLE_MAIN_MENU'

// REDUCER
const menuReducer = (state = false, action) => {
  switch (action.type) {
    case TOGGLE_MAIN_MENU:
      return !state
    default:
      return state
  }
}

// ACTION CREATORS
export const toggleMainMenu = () => ({
  type: TOGGLE_MAIN_MENU,
})

export default menuReducer
