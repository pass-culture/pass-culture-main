import createCachedSelector from 're-reselect'

function mapArgsToCacheKey(state, stockId) {
  return stockId || ''
}

export const selectStockById = createCachedSelector(
  state => state.data.stocks,
  (state, stockId) => stockId,
  (stocks, stockId) => stocks.find(stock => stock.id === stockId)
)(mapArgsToCacheKey)

export default selectStockById
