import createCachedSelector from 're-reselect'

import selectBookingByMatch from './selectBookingByMatch'
import selectMediationByMatch from './selectMediationByMatch'
import selectOfferByMatch from './selectOfferByMatch'
import getIsFinished from '../helpers/getIsFinished'

function mapArgsToCacheKey(state, match) {
  const { params } = match
  const { bookingId, favoriteId, mediationId, offerId } = params
  return `${bookingId || ' '}${favoriteId || ' '}${mediationId || ' '}${offerId || ' '}`
}

const selectIsFinishedByMatch = createCachedSelector(
  selectOfferByMatch,
  selectMediationByMatch,
  selectBookingByMatch,
  getIsFinished
)(mapArgsToCacheKey)

export default selectIsFinishedByMatch
