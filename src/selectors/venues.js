import createCachedSelector from 're-reselect'

function mapArgsToKey(state, optionalOffererId, optionalOfferType) {
  return `${optionalOffererId || ''}/${optionalOfferType || ''}`
}

export default createCachedSelector(
  state => state.data.venues,
  (state, optionalOffererId) => optionalOffererId,
  (state, optionalOffererId, optionalOfferType) => optionalOfferType,
  (venues, optionalOffererId, optionalOfferType) => {
    let filteredVenues = venues

    if (optionalOffererId)
      filteredVenues = filteredVenues.filter(
        v => v.managingOffererId === optionalOffererId
      )

    if (optionalOfferType) {
      if (optionalOfferType.offlineOnly)
        filteredVenues = filteredVenues.filter(v => !v.isVirtual)
      else if (optionalOfferType.onlineOnly)
        filteredVenues = filteredVenues.filter(v => v.isVirtual)
    }

    return filteredVenues
  }
)(mapArgsToKey)
