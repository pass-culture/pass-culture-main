import createCachedSelector from 're-reselect'

function mapArgsToKey(state, offerId, eventOccurrences) {
  return `${offerId || ''}/${
    eventOccurrences ? eventOccurrences.map(eo => eo.id).join('_') : ''
  }`
}

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
)(mapArgsToKey)
