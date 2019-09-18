import createCachedSelector from 're-reselect'

import selectBookingByRouterMatch from './selectBookingByRouterMatch'
import selectMediationByRouterMatch from './selectMediationByRouterMatch'
import selectOfferByRouterMatch from './selectOfferByRouterMatch'
import { ICONS_URL } from '../utils/config'

export const DEFAULT_THUMB_URL = `${ICONS_URL}/picto-placeholder-visueloffre.svg`

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
    if (offer && offer.product.thumbCount) {
      return offer.product.thumbUrl
    }
    return DEFAULT_THUMB_URL
  }
)(mapArgsToCacheKey)

export default selectThumbUrlByRouterMatch
