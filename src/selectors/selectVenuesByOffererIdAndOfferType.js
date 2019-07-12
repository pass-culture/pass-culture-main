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
      filteredVenues = filteredVenues.filter(v => v.managingOffererId === optionalOffererId)

    if (optionalOfferType) {
      if (optionalOfferType.offlineOnly) filteredVenues = filteredVenues.filter(v => !v.isVirtual)
      else if (optionalOfferType.onlineOnly)
        filteredVenues = filteredVenues.filter(v => v.isVirtual)
    }

    return filteredVenues
  }
)(mapArgsToCacheKey)

export default selectVenuesByOffererIdAndOfferType
