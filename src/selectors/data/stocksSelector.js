import createCachedSelector from 're-reselect'
import selectStocksByOfferId from '../selectStocksByOfferId'

export const selectStocks = state => state.data.stocks

export const selectIsEnoughStockForOfferDuo = createCachedSelector(
  (state, offerId) => offerId,
  selectStocksByOfferId,
  (offerId, stocks) => {
    const stocksAvailableForOfferDuo = stocks.filter(
      stock => stock.available === null || stock.available >= 2
    )
    return stocksAvailableForOfferDuo.length > 0 ? true : false
  }
)((state, offerId) => offerId || '')
