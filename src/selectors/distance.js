import { createSelector } from 'reselect'
import get from 'lodash.get';

import selectOffer from './offer'
import selectVenue from './venue'
import { distanceInMeters } from '../utils/geolocation'

export default createSelector(
  selectOffer,
  selectVenue,
  (state) => state.geolocation.position,
  (offer, venue, position) => {
    if (!position || !offer || ! venue) {
      return '?'
    }
    const { latitude, longitude } = position.coords
    const distance = distanceInMeters(latitude, longitude, venue.latitude, venue.longitude)
    if (distance<30) {
      return Math.round(distance)+"m"
    } else if (distance<100) {
      return Math.round(distance/5)*5+"m"
    } else if (distance<1000) {
      return Math.round(distance/10)*10+"m"
    } else {
      return Math.round(distance/100)/10+"km"
    }
  }
)
