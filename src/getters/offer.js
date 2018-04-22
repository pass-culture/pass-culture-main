import get from 'lodash.get'

export default function getOffer(recommendation, offerId) {
  return get(recommendation, 'recommendationOffers', []).find(
    o => (offerId ? o.id === offerId : true)
  )
}
