import createCachedSelector from 're-reselect'
import { createSelector } from 'reselect'

export const selectVenues = state => state.data.venues

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

export const selectVenuesByOffererIdAndOfferType = createCachedSelector(
  selectVenuesByOffererId,
  (state, offererId, offerType = null) => offerType,
  (venuesByOfferId, offerType) => {
    if (offerType) {
      if (offerType.offlineOnly) {
        return venuesByOfferId.filter(venue => !venue.isVirtual)
      } else if (offerType.onlineOnly) {
        return venuesByOfferId.filter(venue => venue.isVirtual)
      }
    }
    return venuesByOfferId
  }
)((state, offererId = '', offerType = '') => `${offererId}/${offerType}`)

export const selectPhysicalVenuesByOffererId = createCachedSelector(
  selectVenuesByOffererId,
  venues => venues.filter(venue => !venue.isVirtual)
)((state, offererId = '') => offererId)

export const selectVenueById = createCachedSelector(
  selectVenues,
  (state, venueId) => venueId,
  (venues, venueId) => venues.find(venue => venue.id === venueId)
)((state, venueId = '') => venueId)

export const selectNonVirtualVenues = createSelector(
  state => state.data.venues || [],
  venues => venues.filter(venue => venue.isVirtual === false)
)
