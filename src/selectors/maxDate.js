import createCachedSelector from 're-reselect'

import occurrencesSelector from './occurrences'

export default createCachedSelector(
  (state, offerId) => occurrencesSelector(state, offerId),
  occurrences => {
    return occurrences.reduce(
      (max, d) =>
        max && max.isAfter(d.beginningDatetimeMoment)
          ? max
          : d.beginningDatetimeMoment,
      null
    )
  }
)((state, offerId) => offerId || '')
