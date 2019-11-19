import createCachedSelector from 're-reselect'

import getIsNotBookable from '../helpers/getIsNotBookable'
import { selectBookingByRouterMatch } from './data/bookingsSelectors'
import { selectMediationByRouterMatch } from './data/mediationsSelectors'
import { selectOfferByRouterMatch } from './data/offersSelectors'

// we did not manage to move this method to bookingsSelectors nor offersSelectors because of circular dependencies
export const selectIsNotBookableByRouterMatch = createCachedSelector(
  selectOfferByRouterMatch,
  selectMediationByRouterMatch,
  selectBookingByRouterMatch,
  getIsNotBookable
)((state, match) => {
  const { params } = match
  const { bookingId, favoriteId, mediationId, offerId } = params
  return `${bookingId || ' '}${favoriteId || ' '}${mediationId || ' '}${offerId || ' '}`
})
