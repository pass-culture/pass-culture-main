import createCachedSelector from 're-reselect'

import { selectBookingById } from '../data/bookingsSelectors'
import { selectFavoriteById } from './favoritesSelectors'

export const selectMediationById = createCachedSelector(
  state => state.data.mediations,
  (state, mediationId) => mediationId,
  (mediations, mediationId) => mediations.find(mediation => mediation.id === mediationId)
)((state, mediationId = '') => mediationId)

export const selectMediationByRouterMatch = createCachedSelector(
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
)((state, match) => {
  const { params } = match
  const { bookingId, favoriteId, mediationId } = params

  return `${bookingId || ' '}${favoriteId || ' '}${mediationId || ' '}`
})

export const
  selectMediationByOfferId = createCachedSelector(
  state => state.data.mediations,
  (state, offerId) => offerId,
  (mediations, offerId) => {
    return mediations.find(mediation => mediation.offerId === offerId)
  }
)((state, offerId) => offerId)
