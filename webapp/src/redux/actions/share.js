export const TOGGLE_SHARE_POPIN = 'TOGGLE_SHARE_POPIN'

export const openSharePopin = (options = null) => ({
  options,
  type: TOGGLE_SHARE_POPIN,
})

export const closeSharePopin = () => ({
  options: null,
  type: TOGGLE_SHARE_POPIN,
})
