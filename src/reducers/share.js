const TOGGLE_SHARE_POPIN = 'TOGGLE_SHARE_POPIN'

export const openSharePopin = (options = null) => ({
  options,
  type: TOGGLE_SHARE_POPIN,
})

export const closeSharePopin = () => ({
  options: false,
  type: TOGGLE_SHARE_POPIN,
})

const defaultValue = { options: false, visible: false }
// TODO -> Trouver un nom plus "debuggable" que le nom `share`
// pour avoir une idée plus claire de ce que fait ce reducer
export const share = (state = defaultValue, action) => {
  switch (action.type) {
    case TOGGLE_SHARE_POPIN:
      return { options: action.options, visible: Boolean(action.options) }
    default:
      return state
  }
}
