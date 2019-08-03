import createCachedSelector from 're-reselect'

import selectOfferByMatch from './selectOfferByMatch'
import { getHumanizeRelativeDistance } from '../utils/geolocation'

function mapArgsToCacheKey(state, match) {
  const { params } = match
  const { bookingId, favoriteId, offerId } = params
  return `${bookingId || ' '}${favoriteId || ' '}${offerId || ' '}`
}

const selectDistanceByMatch = createCachedSelector(
  selectOfferByMatch,
  state => state.geolocation.latitude,
  state => state.geolocation.longitude,
  (offer, userLatitude, userLongitude) => {
    const { venue } = offer || {}
    const { latitude: venueLatitude, longitude: venueLongitude } = venue || {}
    return getHumanizeRelativeDistance(venueLatitude, venueLongitude, userLatitude, userLongitude)
  }
)(mapArgsToCacheKey)

export default selectDistanceByMatch
