import createCachedSelector from 're-reselect'

import selectOffererById from './selectOffererById'
import selectVenueById from './selectVenueById'

function mapArgsToCacheKey(state, venueId, offererId) {
  return `${venueId || ''}${offererId || ''}`
}

const getTimezoneFromDepartementCode = departementCode => {
  switch (departementCode) {
    case '97':
    case '973':
      return 'America/Cayenne'
    default:
      return 'Europe/Paris'
  }
}

export const selectTimezoneByVenueIdAndOffererId = createCachedSelector(
  selectVenueById,
  (state, venueId, offererId) => selectOffererById(state, offererId),
  (venue, offerer) => {
    if (!venue) return

    if (!venue.isVirtual)
      return getTimezoneFromDepartementCode(venue.departementCode)

    if (!offerer) return

    return getTimezoneFromDepartementCode(offerer.postalCode.slice(0, 2))
  }
)(mapArgsToCacheKey)

export default selectTimezoneByVenueIdAndOffererId
