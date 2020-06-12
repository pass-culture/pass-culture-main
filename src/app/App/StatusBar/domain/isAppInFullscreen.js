export const isAppInFullscreen = () => {
  const isiOSAppInFullscreen = window.navigator.standalone
  const isAndroidAppInFullscreen = window.matchMedia('(display-mode: standalone)').matches

  return isAndroidAppInFullscreen || isiOSAppInFullscreen
}
