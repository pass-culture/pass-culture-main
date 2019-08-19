const FAVORITES_EDIT_MODE = 'FAVORITES_EDIT_MODE'
const initialState = {
  edit: false,
  data: [],
}

const favorites = (state = initialState, action) => {
  switch (action.type) {
    case FAVORITES_EDIT_MODE:
      return Object.assign({}, state, {
        edit: !state.edit,
        data: [],
      })
    default:
      return state
  }
}

export const toggleFavoritesEditMode = () => ({
  type: FAVORITES_EDIT_MODE,
})

export default favorites
