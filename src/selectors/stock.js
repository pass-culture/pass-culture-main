import createCachedSelector from 're-reselect'

import stocksSelector from './stocks'

export default createCachedSelector(
  (state, offerId, eventOccurrence) =>
    stocksSelector(state, offerId, eventOccurrence && [eventOccurrence]),
  (state, offerId) => offerId,
  stocks => stocks && stocks[0]
)(
  (state, offerId, eventOccurrence) =>
    `${offerId}/${eventOccurrence && eventOccurrence.id}` || ''
)
