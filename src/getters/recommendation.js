import getMediation from './mediation'
import getOffer from './offer'
import getSource from './source'
import getThumbUrl from './thumbUrl'

export default function getRecommendation(config = {}) {
  const { offerId, recommendation } = config
  if (!recommendation) {
    return
  }
  // FIND THE ASSOCIATED OFFER
  let offer
  if (offerId) {
    offer = getOffer(recommendation, offerId)
  } else {
    const userMediationOffers = recommendation.userMediationOffers
    if (
      recommendation.userMediationOffers &&
      recommendation.userMediationOffers.length
    ) {
      const randomOfferId =
        userMediationOffers[
          Math.floor(Math.random() * userMediationOffers.length)
        ].id
      offer = getOffer(recommendation, randomOfferId)
    }
  }
  // GET OTHER PROPERTIES
  const mediation = getMediation(recommendation)
  const source = getSource(mediation, offer)
  const thumbUrl = getThumbUrl(mediation, source, offer)
  return Object.assign(
    {
      mediation,
      offer,
      thumbUrl,
    },
    recommendation
  )
}
