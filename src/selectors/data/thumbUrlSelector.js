import createCachedSelector from 're-reselect'

import { selectBookingByRouterMatch } from './bookingsSelectors'
import { selectMediationByRouterMatch } from './mediationsSelectors'
import { selectOfferByRouterMatch } from './offersSelectors'

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

    if (offer && offer.product.thumbUrl) {
      return offer.product.thumbUrl
    }
  }
)((state, match) => {
  const { params } = match
  const { bookingId, favoriteId, mediationId, offerId } = params
  return `${bookingId || ' '}${favoriteId || ' '}${mediationId || ' '}${offerId || ' '}`
})
