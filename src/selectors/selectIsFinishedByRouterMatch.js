import createCachedSelector from 're-reselect'

import selectBookingByRouterMatch from './selectBookingByRouterMatch'
import selectMediationByRouterMatch from './selectMediationByRouterMatch'
import selectOfferByRouterMatch from './selectOfferByRouterMatch'
import getIsFinished from '../helpers/getIsFinished'

function mapArgsToCacheKey(state, match) {
  const { params } = match
  const { bookingId, favoriteId, mediationId, offerId } = params
  return `${bookingId || ' '}${favoriteId || ' '}${mediationId || ' '}${offerId || ' '}`
}

const selectIsFinishedByRouterMatch = createCachedSelector(
  selectOfferByRouterMatch,
  selectMediationByRouterMatch,
  selectBookingByRouterMatch,
  getIsFinished
)(mapArgsToCacheKey)

export default selectIsFinishedByRouterMatch
