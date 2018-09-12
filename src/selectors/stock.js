import createCachedSelector from 're-reselect'

import stocksSelector from './stocks'

export default createCachedSelector(
  stocksSelector,
  (state, offerId) => offerId,
  (state, offerId, eventOccurrenceId) => eventOccurrenceId,
  (stocks, offerId, eventOccurrenceId) =>
    stocks.find(stock => stock.eventOccurrenceId === eventOccurrenceId)
)((state, eventOccurrenceId) => eventOccurrenceId || '')
