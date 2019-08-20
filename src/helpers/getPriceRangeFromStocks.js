import uniq from 'lodash.uniq'

const getPriceRangeFromStocks = stocks => {
  if (!stocks || !Array.isArray(stocks)) return []
  const pricesForAvailableStocks = stocks
    .filter(stock => stock.price >= 0)
    .filter(stock => stock.isBookable)
    .filter(stock => stock.available === null || stock.available > 0)
    .map(stock => stock.price)

  if (pricesForAvailableStocks.length === 0) {
    return []
  }

  const minimum_price = Math.min(...pricesForAvailableStocks)
  const maximum_price = Math.max(...pricesForAvailableStocks)

  return uniq([minimum_price, maximum_price])
}

export default getPriceRangeFromStocks
