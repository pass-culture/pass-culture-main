import createCachedSelector from 're-reselect'

import selectVenueById from './selectVenueById'

function mapArgsToCacheKey(state, venueId) {
  return venueId || ''
}

export const selectTimezoneByVenueId = createCachedSelector(
  (state, venueId) => selectVenueById(state, venueId),
  venue => {
    if (!venue) return
    switch (venue.departementCode) {
      case '97':
      case '973':
        return 'America/Cayenne' // POSIX compatibility requires that the offsets are inverted.
      default:
        return 'Europe/Paris'
    }
  }
)(mapArgsToCacheKey)

export default selectTimezoneByVenueId
