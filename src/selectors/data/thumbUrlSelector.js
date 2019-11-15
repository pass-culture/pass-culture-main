import createCachedSelector from 're-reselect'
import { selectMediationByRouterMatch } from './mediationSelectors'
import { selectBookingByRouterMatch } from './bookingsSelectors'
import { selectOfferByRouterMatch } from './offersSelectors'

function mapArgsToCacheKey(state, match) {
  const { params } = match
  const { bookingId, favoriteId, mediationId, offerId } = params
  return `${bookingId || ' '}${favoriteId || ' '}${mediationId || ' '}${offerId || ' '}`
}

export const selectThumbUrlByRouterMatch = createCachedSelector(
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
