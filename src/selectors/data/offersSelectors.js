import createCachedSelector from 're-reselect'
import { selectVenuesByOffererId } from './venuesSelectors'
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

export const selectOffersByOffererIdAndVenueId = createCachedSelector(
  state => state.data.offers,
  (state, offererId) => offererId && selectVenuesByOffererId(state, offererId),
  (state, offererId, venueId) => venueId,
  (offers, venues, venueId) => {
    const venueIds = [].concat(venueId || (venues || []).map(v => v.id))
    return offers.filter(o => (venueIds.length ? venueIds.includes(o.venueId) : true))
  }
)((state, offererId = '', venueId = '') => `${offererId}/${venueId}`)

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
