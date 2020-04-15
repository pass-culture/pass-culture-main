export const SHOW_SPLASH = 'SHOW_SPLASH'
export const CLOSE_SPLASH = 'CLOSE_SPLASH'

export const closeSplash = () => {
  return { type: CLOSE_SPLASH }
}

export const showSplash = () => {
  return { type: SHOW_SPLASH }
}
