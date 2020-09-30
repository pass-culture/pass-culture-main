import createCachedSelector from 're-reselect'
import { createSelector } from 'reselect'

export const selectOfferById = createCachedSelector(
  state => state.data.offers,
  (state, offerId) => offerId,
  (offers, offerId) => {
    if (offers) {
      return offers.find(offer => offer.id === offerId)
    }
  }
)((state, offerId = '') => offerId)

export const selectOffers = state => state.data.offers

export const selectDigitalOffers = createSelector(
  state => state.data.offers || [],
  offers => offers.filter(offer => offer.isDigital)
)

function mapArgsToCacheKey(state, venueId) {
  return venueId || ''
}

export const selectOffersByVenueId = createCachedSelector(
  state => state.data.offers || [],
  (state, venueId) => venueId,
  (offers, venueId) => offers.filter(offer => offer.venueId === venueId)
)(mapArgsToCacheKey)
