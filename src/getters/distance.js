import get from 'lodash.get'

import getOffer from './offer'
import getSource from './source'
import getVenue from './venue'

import { distanceInMeters } from '../utils/geolocation'

export default function getDistance(recommendation, latitude, longitude) {
  const offer = getOffer(recommendation, null)
  const source = getSource(recommendation.mediation, offer)
  const venue = getVenue(source, offer)
  // console.log('recommendation', recommendation, offer, source, venue)
  return typeof get(recommendation, 'mediation.tutoIndex') === 'number'
    ? -(1 / (recommendation.mediation.tutoIndex + 1))
    : venue
      ? distanceInMeters(latitude, longitude, venue.latitude, venue.longitude)
      : 10000000
}
