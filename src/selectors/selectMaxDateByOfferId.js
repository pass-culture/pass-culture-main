import createCachedSelector from 're-reselect'

import selectStocksByOfferId from './selectStocksByOfferId'

function mapArgsToCacheKey(state, offerId) {
  return offerId || ''
}

export const selectMaxDateByOfferId = createCachedSelector(
  selectStocksByOfferId,
  stocks => {
    return stocks.reduce(
      (max, stock) =>
        max && max.isAfter(stock.beginningDatetimeMoment)
          ? max
          : stock.beginningDatetimeMoment,
      null
    )
  }
)(mapArgsToCacheKey)

export default selectMaxDateByOfferId
