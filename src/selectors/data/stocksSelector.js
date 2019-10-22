import createCachedSelector from 're-reselect'
import selectOfferById from '../selectOfferById'
import selectStocksByOfferId from '../selectStocksByOfferId'
import selectStockById from '../selectStockById'
import selectIsFeatureDisabled from '../../components/router/selectors/selectIsFeatureDisabled'

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

export const selectIsStockDuo = createCachedSelector(
  selectStockById,
  (state, stockId, offerId) => selectOfferById(state, offerId),
  (state, stockId, offerId, featureName) => selectIsFeatureDisabled(state, featureName),
  (stock, offer, isFeatureDisabled) => {
    const isEnoughAvailable = stock && (stock.available >= 2 || stock.available === null)
    const isOfferDuo = offer && offer.isDuo
    const isStockDuo = !isFeatureDisabled && isEnoughAvailable && isOfferDuo

    return isStockDuo
  }
)((state, stockId) => stockId || '')
