import createCachedSelector from 're-reselect'

import { selectBookingByRouterMatch } from './data/bookingsSelector'
import selectMediationByRouterMatch from './selectMediationByRouterMatch'
import { selectOfferByRouterMatch } from './data/offersSelector'
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
