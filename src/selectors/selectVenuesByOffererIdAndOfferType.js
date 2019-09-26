import createCachedSelector from 're-reselect'

function mapArgsToCacheKey(state, optionalOffererId, optionalOfferType) {
  return `${optionalOffererId || ''}/${optionalOfferType || ''}`
}

const selectVenuesByOffererIdAndOfferType = createCachedSelector(
  state => state.data.venues,
  (state, optionalOffererId) => optionalOffererId,
  (state, optionalOffererId, optionalOfferType) => optionalOfferType,
  (venues, optionalOffererId, optionalOfferType) => {
    let filteredVenues = venues

    if (optionalOffererId)
      filteredVenues = filteredVenues.filter(venue => venue.managingOffererId === optionalOffererId)

    if (optionalOfferType) {
      if (optionalOfferType.offlineOnly) filteredVenues = filteredVenues.filter(venue => !venue.isVirtual)
      else if (optionalOfferType.onlineOnly)
        filteredVenues = filteredVenues.filter(venue => venue.isVirtual)
    }

    return filteredVenues
  }
)(mapArgsToCacheKey)

export default selectVenuesByOffererIdAndOfferType
