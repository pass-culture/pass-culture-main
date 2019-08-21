const FAVORITES_TOGGLE_EDIT_MODE = 'FAVORITES_TOGGLE_EDIT_MODE'
const FAVORITES_TOGGLE_UPDATE = 'FAVORITES_TOGGLE_UPDATE'
const initialState = {
  edit: false,
  data: [],
}

const favorites = (state = initialState, action) => {
  let isUpdated = true

  switch (action.type) {
    case FAVORITES_TOGGLE_EDIT_MODE:
      return {
        ...state,
        ...{
          edit: !state.edit,
          data: [],
        },
      }

    case FAVORITES_TOGGLE_UPDATE:
      state.data = state.data.reduce((favoritesToDelete, currentFavorite) => {
        if (currentFavorite === action.offerId) {
          isUpdated = false
        } else {
          favoritesToDelete.push(currentFavorite)
        }

        return favoritesToDelete
      }, [])

      if (isUpdated) {
        state.data.push(action.offerId)
      }

      return {
        ...state,
        ...{
          edit: state.edit,
          data: state.data,
        },
      }

    default:
      return state
  }
}

export const toggleFavoritesEditMode = () => ({
  type: FAVORITES_TOGGLE_EDIT_MODE,
})

export const handleToggleFavorite = offerId => ({
  offerId,
  type: FAVORITES_TOGGLE_UPDATE,
})

export default favorites
