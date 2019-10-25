import createCachedSelector from 're-reselect'

import { selectBookingByRouterMatch } from './data/bookingsSelector'
import selectMediationByRouterMatch from './selectMediationByRouterMatch'
import { selectOfferByRouterMatch } from './data/offersSelector'

function mapArgsToCacheKey(state, match) {
  const { params } = match
  const { bookingId, favoriteId, mediationId, offerId } = params
  return `${bookingId || ' '}${favoriteId || ' '}${mediationId || ' '}${offerId || ' '}`
}

const selectThumbUrlByRouterMatch = createCachedSelector(
  selectMediationByRouterMatch,
  selectBookingByRouterMatch,
  selectOfferByRouterMatch,
  (mediation, booking, offer) => {
    if (mediation) {
      return mediation.thumbUrl
    }
    if (booking && booking.thumbUrl) {
      return booking.thumbUrl
    }
    if (offer && offer.product.thumbCount >= 0) {
      return offer.product.thumbUrl
    }
  }
)(mapArgsToCacheKey)

export default selectThumbUrlByRouterMatch
