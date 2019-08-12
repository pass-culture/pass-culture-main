import createCachedSelector from 're-reselect'

import selectMediationByRouterMatch from './selectMediationByRouterMatch'
import selectOfferByRouterMatch from './selectOfferByRouterMatch'

function mapArgsToCacheKey(state, match) {
  const { params } = match
  const { bookingId, favoriteId, mediationId, offerId } = params
  return `${bookingId || ' '}${favoriteId || ' '}${mediationId || ' '}${offerId || ' '}`
}

const selectThumbUrlByRouterMatch = createCachedSelector(
  selectMediationByRouterMatch,
  selectOfferByRouterMatch,
  (mediation, offer) => {
    if (mediation) {
      return mediation.thumbUrl
    }
    if (offer) {
      return offer.product.thumbUrl
    }
  }
)(mapArgsToCacheKey)

export default selectThumbUrlByRouterMatch
