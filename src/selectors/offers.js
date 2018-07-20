import createCachedSelector from 're-reselect'

import {resolveDataCollection} from '../utils/resolvers'

import occurencesSelector from './occurences'

export default createCachedSelector(
  state => state.data.offers,
  (state, venueId, eventId) => occurencesSelector(state, venueId, eventId),
  (offers, occurences) =>
    resolveDataCollection(offers, 'offers').filter(offer =>
      occurences.some(occurence => offer.eventOccurenceId === occurence.id)
    )
)(
  (state, venueId, eventId) => `${venueId || ''}/${eventId || ''}`
)
