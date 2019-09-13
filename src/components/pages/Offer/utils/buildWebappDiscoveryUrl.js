export const buildWebappDiscoveryUrl = (offerId, mediationId) => {
  const currentUrl = window.location.href
  let webappUrl
  if (currentUrl.includes('pro')) {
    webappUrl = currentUrl.split('offres')[0].replace('pro', 'app')
  } else {
    webappUrl = 'http://localhost:3000/'
  }
  return webappUrl + 'decouverte/' + offerId + '/' + mediationId
}
