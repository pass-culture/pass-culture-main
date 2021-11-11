export const trackEventWrapper = data => {
  const Matomo = window._paq || []
  Matomo.push(['trackEvent', data.page, data.action, data.name])
}
