import createCachedSelector from 're-reselect';

import createOccurencesSelector from './createOccurences'

export default createCachedSelector(
  createOccurencesSelector(),
  occurences => {
    return occurences
      .reduce((max, d) => max &&
        max.isAfter(d.beginningDatetimeMoment) ? max : d.beginningDatetimeMoment, null
      )
  },
  (state, venueId, eventId) => `${venueId}/${eventId}`
)
