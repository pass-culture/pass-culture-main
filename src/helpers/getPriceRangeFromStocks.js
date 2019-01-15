const getPriceRangeFromStocks = stocks => {
  if (!stocks || !Array.isArray(stocks)) return []

  const filtered = stocks
    .filter(stock => stock.available === null || stock.available > 0)
    .map(stock => stock.price)
  return filtered
}

export default getPriceRangeFromStocks
