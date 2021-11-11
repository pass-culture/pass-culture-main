export const isAppInFullscreen = () => {
  const isIosAppInFullscreen = window.navigator.standalone
  const isAndroidAppInFullscreen = window.matchMedia('(display-mode: standalone)').matches

  return isAndroidAppInFullscreen || isIosAppInFullscreen
}
