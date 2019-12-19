import createCachedSelector from 're-reselect'

import { getHumanizeRelativeDistance } from '../utils/geolocation'
import { selectOfferById, selectOfferByRouterMatch } from './data/offersSelectors'

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
)((state, offerId = '') => offerId)

export const selectDistanceByRouterMatch = createCachedSelector(
  selectOfferByRouterMatch,
  state => state.geolocation.latitude,
  state => state.geolocation.longitude,
  (offer, userLatitude, userLongitude) => {
    const { venue } = offer || {}
    const { latitude: venueLatitude, longitude: venueLongitude } = venue || {}
    return getHumanizeRelativeDistance(venueLatitude, venueLongitude, userLatitude, userLongitude)
  }
)((state, match) => {
  const { params } = match
  const { bookingId, favoriteId, offerId } = params
  return `${bookingId || ' '}${favoriteId || ' '}${offerId || ' '}`
})

export const selectUserGeolocation = state => state.geolocation
