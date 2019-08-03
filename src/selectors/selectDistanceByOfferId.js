import createCachedSelector from 're-reselect'

import selectOfferById from './selectOfferById'
import { getHumanizeRelativeDistance } from '../utils/geolocation'

function mapArgsToCacheKey(state, offerId) {
  return offerId || ''
}

export const selectDistanceByOfferId = createCachedSelector(
  selectOfferById,
  state => state.geolocation.latitude,
  state => state.geolocation.longitude,
  (offer, userLatitude, userLongitude) => {
    const { venue } = offer || {}
    const { latitude: venueLatitude, longitude: venueLongitude } = venue || {}
    const distance = getHumanizeRelativeDistance(
      venueLatitude,
      venueLongitude,
      userLatitude,
      userLongitude
    )
    return distance
  }
)(mapArgsToCacheKey)

export default selectDistanceByOfferId
