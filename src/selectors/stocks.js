import createCachedSelector from 're-reselect'

export default createCachedSelector(
  state => state.data.stocks,
  (state, offerId) => offerId,
  (state, offerId, eventOccurrenceId) => eventOccurrenceId,
  (stocks, offerId, eventOccurrenceId) =>
    stocks.filter(
      stock =>
        stock.offerId === offerId ||
        stock.eventOccurrenceId === eventOccurrenceId
    )
)(
  (state, offerId, eventOccurrenceId) =>
    `${offerId || ''}/${eventOccurrenceId || ''}`
)
