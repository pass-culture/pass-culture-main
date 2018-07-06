import createCachedSelector from 're-reselect';

import occurencesSelector from './occurences'

export default createCachedSelector(
  (state, venueId, eventId) => occurencesSelector(state, venueId, eventId),
  occurences => {
    return occurences
      .reduce((max, d) => max &&
        max.isAfter(d.beginningDatetimeMoment) ? max : d.beginningDatetimeMoment, null
      )
  },
  (state, venueId, eventId) => `${venueId}/${eventId}`
)
