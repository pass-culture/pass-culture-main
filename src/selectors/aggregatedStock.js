import createCachedSelector from 're-reselect'

import stocksSelector from './stocks'

export default createCachedSelector(stocksSelector, stocks =>
  stocks.reduce(
    (aggreged, stock) => ({
      available: aggreged.available + stock.available,
      groupSizeMin: aggreged.groupSizeMin
        ? Math.min(aggreged.groupSizeMin, stock.groupSize)
        : stock.groupSize,
      groupSizeMax: aggreged.groupSizeMax
        ? Math.max(aggreged.groupSizeMax, stock.groupSize)
        : stock.groupSize,
      priceMin: aggreged.priceMin
        ? Math.min(aggreged.priceMin, stock.price)
        : stock.price,
      priceMax: aggreged.priceMax
        ? Math.max(aggreged.priceMax, stock.price)
        : stock.price,
    }),
    {
      available: 0,
      groupSizeMin: 0,
      groupSizeMax: 0,
      priceMin: 0,
      priceMax: 0,
    }
  )
)(
  (state, offerId, eventOccurrences) =>
    `${offerId || ''}/${
      eventOccurrences ? eventOccurrences.map(eo => eo.id).join('_') : ''
    }`
)
