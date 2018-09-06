import createCachedSelector from 're-reselect'

export default createCachedSelector(
  state => state.data.stocks,
  (state, stockId) => stockId,
  (stocks, stockId) => stocks.find(stock => stock.id === stockId)
)((state, stockId) => stockId || '')
