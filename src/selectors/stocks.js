import createCachedSelector from 're-reselect'

import occurrencesSelector from './occurrences'

export default createCachedSelector(
  state => state.data.stocks,
  (state, offerId) => occurrencesSelector(state, offerId),
  (stocks, occurrences) =>
    stocks.filter(offer =>
      occurrences.some(occurrence => offer.eventOccurrenceId === occurrence.id)
    )
)((state, offerId) => offerId || '')
