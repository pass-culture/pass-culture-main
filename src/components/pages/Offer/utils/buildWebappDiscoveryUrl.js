import { IS_PROD } from '../../../../utils/config'

export const buildWebappDiscoveryUrl = (offerId, mediationId) => {
  const currentUrl = window.location.href
  let webappUrl
  if ( IS_PROD ) {
    webappUrl = currentUrl.split('offres')[0].replace('pro', 'app')
  } else {
    webappUrl = 'http://localhost:3000/'
  }
  return webappUrl + 'decouverte/' + offerId + '/' + mediationId
}
