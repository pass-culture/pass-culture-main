import createCachedSelector from 're-reselect'

import venuesSelector from './venues'

function mapArgsToKey(state, offererId) {
  return `${offererId || ''}`
}

const selectPhysicalVenuesByOffererId = createCachedSelector(
  venuesSelector,
  venues => venues.filter(venue => !venue.isVirtual)
)(mapArgsToKey)

export default selectPhysicalVenuesByOffererId
