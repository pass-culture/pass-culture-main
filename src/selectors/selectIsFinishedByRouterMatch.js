import createCachedSelector from 're-reselect'

import selectBookingByRouterMatch from './selectBookingByRouterMatch'
import selectMediationByMatch from './selectMediationByMatch'
import selectOfferByMatch from './selectOfferByMatch'
import getIsFinished from '../helpers/getIsFinished'

function mapArgsToCacheKey(state, match) {
  const { params } = match
  const { bookingId, favoriteId, mediationId, offerId } = params
  return `${bookingId || ' '}${favoriteId || ' '}${mediationId || ' '}${offerId || ' '}`
}

const selectIsFinishedByRouterMatch = createCachedSelector(
  selectOfferByMatch,
  selectMediationByMatch,
  selectBookingByRouterMatch,
  getIsFinished
)(mapArgsToCacheKey)

export default selectIsFinishedByRouterMatch
