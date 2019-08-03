import createCachedSelector from 're-reselect'

import selectMediationByMatch from './selectMediationByMatch'
import selectOfferByMatch from './selectOfferByMatch'

function mapArgsToCacheKey(state, match) {
  const { params } = match
  const { bookingId, favoriteId, mediationId, offerId } = params
  return `${bookingId || ' '}${favoriteId || ' '}${mediationId || ' '}${offerId || ' '}`
}

const selectThumbUrlByMatch = createCachedSelector(
  selectMediationByMatch,
  selectOfferByMatch,
  (mediation, offer) => {
    if (mediation) {
      return mediation.thumbUrl
    }
    if (offer) {
      return offer.product.thumbUrl
    }
  }
)(mapArgsToCacheKey)

export default selectThumbUrlByMatch
