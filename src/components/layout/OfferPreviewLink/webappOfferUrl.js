import { IS_PROD } from 'utils/config'

export const webappOfferUrl = (offerId, mediationId = undefined) => {
  const webappUrl = IS_PROD ? window.location.href.split('offres')[0].replace('pro', 'app') : 'http://localhost:3000/'
  const urlWithOfferId = `${webappUrl}offre/details/${offerId}`

  return mediationId ? `${urlWithOfferId}/${mediationId}` : urlWithOfferId
}
