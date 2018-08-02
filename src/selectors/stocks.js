import createCachedSelector from 're-reselect'

import occurrencesSelector from './occurrences'

export default createCachedSelector(
  state => state.data.stocks,
  (state, venueId, eventId) => occurrencesSelector(state, venueId, eventId),
  (stocks, occurrences) =>
    stocks.filter(offer =>
      occurrences.some(occurrence => offer.eventOccurrenceId === occurrence.id)
    )
)((state, venueId, eventId) => `${venueId || ''}/${eventId || ''}`)
