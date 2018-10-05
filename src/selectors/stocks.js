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

// Can't understand previous selector (eventOccurences ??)
// Creating a new one, no re-reselect, lib hurts brain and is premature optim' anyway
// I mean, isn't this way more readable (beyond being effective)?
export const getStockByOfferId = (state, offerId) =>
  state.data.stocks.filter(item => item.offerId === offerId)
