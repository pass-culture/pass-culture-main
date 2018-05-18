import { createSelector } from 'reselect'

import selectCurrentOffer from './currentOffer'
import selectCurrentVenue from './currentVenue'
import { distanceInMeters } from '../utils/geolocation'

export default createSelector(
  selectCurrentOffer,
  selectCurrentVenue,
  state => state.geolocation.latitude,
  state => state.geolocation.longitude,
  (offer, venue, latitude, longitude) => {
    if (!latitude || !longitude || !offer || !venue) {
      return '-'
    }
    const distance = distanceInMeters(
      latitude,
      longitude,
      venue.latitude,
      venue.longitude
    )
    if (distance < 30) {
      return Math.round(distance) + ' m'
    } else if (distance < 100) {
      return Math.round(distance / 5) * 5 + ' m'
    } else if (distance < 1000) {
      return Math.round(distance / 10) * 10 + ' m'
    } else if (distance < 5000) {
      return Math.round(distance / 100) / 10 + ' km'
    } else {
      return Math.round(distance / 1000) + ' km'
    }
  }
)
