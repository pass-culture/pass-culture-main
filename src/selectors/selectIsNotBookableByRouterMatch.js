import createCachedSelector from 're-reselect'

import selectBookingByRouterMatch from './selectBookingByRouterMatch'
import selectMediationByRouterMatch from './selectMediationByRouterMatch'
import selectOfferByRouterMatch from './selectOfferByRouterMatch'
import getIsNotBookable from '../helpers/getIsNotBookable'

function mapArgsToCacheKey(state, match) {
  const { params } = match
  const { bookingId, favoriteId, mediationId, offerId } = params
  return `${bookingId || ' '}${favoriteId || ' '}${mediationId || ' '}${offerId || ' '}`
}

const selectIsNotBookableByRouterMatch = createCachedSelector(
  selectOfferByRouterMatch,
  selectMediationByRouterMatch,
  selectBookingByRouterMatch,
  getIsNotBookable
)(mapArgsToCacheKey)

export default selectIsNotBookableByRouterMatch
