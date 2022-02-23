import get from 'lodash.get'
import createCachedSelector from 're-reselect'

export const selectVenues = state => get(state, 'data.venues', [])

function hasMananingOffererId(venue, offererId) {
  if (venue.managingOfferer) {
    return venue.managingOfferer.id == offererId
  } else return venue.managingOffererId == offererId
}

export const selectVenuesByOffererId = createCachedSelector(
  selectVenues,
  (state, offererId = null) => offererId,
  (venues, offererId) => {
    if (offererId) {
      return venues.filter(venue => hasMananingOffererId(venue, offererId))
    }
    return venues
  }
)((state, offererId = '') => offererId)

export const selectPhysicalVenuesByOffererId = createCachedSelector(
  selectVenuesByOffererId,
  venues => venues.filter(venue => !venue.isVirtual)
)((state, offererId = '') => offererId)

export const selectVenueById = createCachedSelector(
  selectVenues,
  (state, venueId) => venueId,
  (venues, venueId) => venues.find(venue => venue.id === venueId)
)((state, venueId = '') => venueId)
