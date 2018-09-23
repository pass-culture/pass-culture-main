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
export const share = (state = defaultValue, action) => {
  switch (action.type) {
    case TOGGLE_SHARE_POPIN:
      return { options: action.options, visible: !!action.options }
    default:
      return state
  }
}
