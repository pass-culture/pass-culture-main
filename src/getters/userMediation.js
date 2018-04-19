import getMediation from './mediation'
import getOffer from './offer'
import getSource from './source'
import getThumbUrl from './thumbUrl'

export default function getUserMediation (config = {}) {
  const {
    offerId,
    userMediation
  } = config
  if (!userMediation) {
    return
  }
  // FIND THE ASSOCIATED OFFER
  let offer
  if (offerId) {
    offer = getOffer(userMediation, offerId)
  } else {
    const userMediationOffers = userMediation.userMediationOffers
    if (userMediation.userMediationOffers && userMediation.userMediationOffers.length) {
      const randomOfferId = userMediationOffers[
        Math.floor(Math.random() * userMediationOffers.length)].id
      offer = getOffer(userMediation, randomOfferId)
    }
  }
  // GET OTHER PROPERTIES
  const mediation = getMediation(userMediation)
  const source = getSource(mediation, offer)
  const thumbUrl = getThumbUrl(mediation, source, offer)
  return Object.assign({
    mediation,
    offer,
    thumbUrl
  }, userMediation)
}
