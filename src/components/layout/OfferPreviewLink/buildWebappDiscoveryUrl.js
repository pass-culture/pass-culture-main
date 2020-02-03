import { IS_PROD } from '../../../utils/config'

export const buildWebappDiscoveryUrl = (offerId, mediationId) => {
  const currentUrl = window.location.href
  let webappUrl = 'http://localhost:3000/'

  if (IS_PROD) {
    webappUrl = currentUrl.split('offres')[0].replace('pro', 'app')
  }

  return `${webappUrl}offre/details/${offerId}/${mediationId}`
}
