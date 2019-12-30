import createCachedSelector from 're-reselect'

import { selectOfferById } from './offersSelectors'

const selectStocks = state => state.data.stocks

export const selectStockById = createCachedSelector(
  selectStocks,
  (state, stockId) => stockId,
  (stocks, stockId) => stocks.find(stock => stock.id === stockId)
)((state, stockId = '') => stockId)

export const selectStocksByOfferId = createCachedSelector(
  selectStocks,
  (state, offerId) => offerId,
  (stocks, offerId) => stocks.filter(stock => stock.offerId === offerId)
)((state, offerId = '') => offerId)

export const selectIsEnoughStockForOfferDuo = createCachedSelector(
  (state, offerId) => offerId,
  selectStocksByOfferId,
  (offerId, stocks) => {
    const stocksAvailableForOfferDuo = stocks.filter(
      stock => stock.available === null || stock.available >= 2
    )
    return stocksAvailableForOfferDuo.length > 0
  }
)((state, offerId) => offerId || '')

export const selectIsStockDuo = createCachedSelector(
  selectStockById,
  (state, stockId, offerId) => selectOfferById(state, offerId),
  (stock, offer) => {
    const isEnoughAvailable = stock && (stock.available >= 2 || stock.available === null)
    const isOfferDuo = offer && offer.isDuo
    const isStockDuo = isEnoughAvailable && isOfferDuo

    return isStockDuo
  }
)((state, stockId) => stockId || '')
