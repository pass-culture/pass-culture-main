import createCachedSelector from 're-reselect'

import occurencesSelector from './occurences'

export default createCachedSelector(
  state => state.data.offers,
  (state, venueId, eventId) => occurencesSelector(state, venueId, eventId),
  (offers, occurences) => {
    return offers.filter(offer => {
      return occurences.some(occurence => offer.eventOccurenceId === occurence.id)
    })
  }
)(
  (state, venueId, eventId) => `${venueId || ''}/${eventId || ''}`
)
