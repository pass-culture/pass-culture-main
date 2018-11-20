const getPriceRangeFromStocks = stocks => {
  if (!stocks || !Array.isArray(stocks)) return []
  const filtered = stocks
    .filter(o => o.available && o.available > 0)
    .map(o => o.price)
  return filtered
}

export default getPriceRangeFromStocks
