import createCachedSelector from 're-reselect'

import selectStocksByOfferId from './selectStocksByOfferId'

function mapArgsToCacheKey(state, offerId) {
  return offerId || ''
}

const selectAggregatedStockByOfferId = createCachedSelector(selectStocksByOfferId, stocks =>
  stocks.reduce(
    (aggregatedStock, stock) => ({
      available: aggregatedStock.available + stock.available,
      groupSizeMin: aggregatedStock.groupSizeMin
        ? Math.min(aggregatedStock.groupSizeMin, stock.groupSize)
        : stock.groupSize,
      groupSizeMax: aggregatedStock.groupSizeMax
        ? Math.max(aggregatedStock.groupSizeMax, stock.groupSize)
        : stock.groupSize,
      priceMin: aggregatedStock.priceMin
        ? Math.min(aggregatedStock.priceMin, stock.price)
        : stock.price,
      priceMax: aggregatedStock.priceMax
        ? Math.max(aggregatedStock.priceMax, stock.price)
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
)(mapArgsToCacheKey)

export default selectAggregatedStockByOfferId
