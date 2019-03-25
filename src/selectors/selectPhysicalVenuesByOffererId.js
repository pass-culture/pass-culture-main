import createCachedSelector from 're-reselect'

import selectVenuesByOffererIdAndOfferType from './selectVenuesByOffererIdAndOfferType'

function mapArgsToCacheKey(state, offererId) {
  return `${offererId || ''}`
}

const selectPhysicalVenuesByOffererId = createCachedSelector(
  selectVenuesByOffererIdAndOfferType,
  venues => venues.filter(venue => !venue.isVirtual)
)(mapArgsToCacheKey)

export default selectPhysicalVenuesByOffererId
