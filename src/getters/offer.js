import get from 'lodash.get'

export default function getOffer(recommendation, offerId) {
  return get(recommendation, 'userMediationOffers', []).find(
    o => (offerId ? o.id === offerId : true)
  )
}
