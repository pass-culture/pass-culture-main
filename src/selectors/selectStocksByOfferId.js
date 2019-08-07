import createCachedSelector from 're-reselect'

function mapArgsToCacheKey(state, offerId) {
  return offerId || ''
}

export const selectStocksByOfferId = createCachedSelector(
  state => state.data.stocks,
  (state, offerId) => offerId,
  (stocks, offerId) => stocks.filter(stock => stock.offerId === offerId)
)(mapArgsToCacheKey)

export default selectStocksByOfferId
