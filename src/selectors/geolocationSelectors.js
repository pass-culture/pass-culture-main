import createCachedSelector from 're-reselect'

import { getHumanizeRelativeDistance } from '../utils/geolocation'
import { selectOfferById, selectOfferByRouterMatch } from './data/offersSelectors'

export const selectUserGeolocation = state => state.geolocation

export const selectDistanceByOfferId = createCachedSelector(
  selectOfferById,
  selectUserGeolocation,
  (offer, userGeolocation) => {
    const { latitude: userLatitude, longitude: userLongitude } = userGeolocation
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
  selectUserGeolocation,
  (offer, userGeolocation) => {
    const { latitude: userLatitude, longitude: userLongitude } = userGeolocation
    const { venue } = offer || {}
    const { latitude: venueLatitude, longitude: venueLongitude } = venue || {}
    return getHumanizeRelativeDistance(venueLatitude, venueLongitude, userLatitude, userLongitude)
  }
)((state, match) => {
  const { params } = match
  const { bookingId, favoriteId, offerId } = params
  return `${bookingId || ' '}${favoriteId || ' '}${offerId || ' '}`
})
