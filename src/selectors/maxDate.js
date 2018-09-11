import createCachedSelector from 're-reselect'

import eventOccurrencesSelector from './eventOccurrences'

export default createCachedSelector(
  (state, offerId) => eventOccurrencesSelector(state, offerId),
  eventOccurrences => {
    return eventOccurrences.reduce(
      (max, d) =>
        max && max.isAfter(d.beginningDatetimeMoment)
          ? max
          : d.beginningDatetimeMoment,
      null
    )
  }
)((state, offerId) => offerId || '')
