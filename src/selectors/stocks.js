import createCachedSelector from 're-reselect'

export default createCachedSelector(
  state => state.data.stocks,
  (state, offerId) => offerId,
  (state, offerId, eventOccurrences) => eventOccurrences,
  (stocks, offerId, eventOccurrences) =>
    stocks.filter(
      stock =>
        eventOccurrences
          ? eventOccurrences.find(eo => eo.id === stock.eventOccurrenceId)
          : stock.offerId === offerId
    )
)(
  (state, offerId, eventOccurrences) =>
    `${offerId || ''}/${
      eventOccurrences ? eventOccurrences.map(eo => eo.id).join('_') : ''
    }`
)
