export const getPriceRangeFromStocks = stocks => {
  if (!Array.isArray(stocks) || !stocks) return []
  const ifAvailable = o => o.available && o.available > 0
  const filtered = stocks.filter(ifAvailable).map(o => o.price)
  return filtered
}

export default getPriceRangeFromStocks
