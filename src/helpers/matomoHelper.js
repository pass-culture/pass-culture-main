export const trackMatomoEventWrapper = data => {
  const Matomo = window._paq || []
  Matomo.push(['trackEvent', data.page, data.action, data.name])
}
