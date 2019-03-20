import createCachedSelector from 're-reselect'

import selectStocksByOfferId from './selectStocksByOfferId'

function mapArgsToKey(state, offerId) {
  return offerId || ''
}

export const selectAggregatedStockByOfferId = createCachedSelector(
  selectStocksByOfferId,
  stocks =>
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
)(mapArgsToKey)

export default selectAggregatedStockByOfferId
