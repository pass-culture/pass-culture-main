import createCachedSelector from 're-reselect'

import selectBookingById from './selectBookingById'
import selectFavoriteById from './selectFavoriteById'
import selectMediationById from './selectMediationById'

function mapArgsToCacheKey(state, match) {
  const { params } = match
  const { bookingId, favoriteId, mediationId } = params

  return `${bookingId || ' '}${favoriteId || ' '}${mediationId || ' '}`
}

const selectMediationByRouterMatch = createCachedSelector(
  state => state.data.mediations,
  (state, match) => selectBookingById(state, match.params.bookingId),
  (state, match) => selectFavoriteById(state, match.params.favoriteId),
  (state, match) => selectMediationById(state, match.params.mediationId),
  (mediations, booking, favorite, mediation) => {
    if (mediation) return mediation

    if (booking && booking.mediationId) {
      return selectMediationById({ data: { mediations } }, booking.mediationId)
    }

    if (favorite) {
      return selectMediationById({ data: { mediations } }, favorite.mediationId)
    }
  }
)(mapArgsToCacheKey)

export default selectMediationByRouterMatch
