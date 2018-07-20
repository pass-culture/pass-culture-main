import createCachedSelector from 're-reselect';

import {resolveDataCollection} from '../utils/resolvers'

export default createCachedSelector(
  state => state.data.venues,
  (state, optionalOffererId) => optionalOffererId,
  (venues, optionalOffererId) => {
    venues = resolveDataCollection(venues, 'venues')
    if (optionalOffererId)
      return venues.filter(v => v.managingOffererId === optionalOffererId)
    return venues
  }
)(
  (state, optionalOffererId) => optionalOffererId || ''
)
