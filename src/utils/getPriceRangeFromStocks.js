const unique = array => array.filter((value, index, array) => index === array.indexOf(value))
const hasPrice = stock => stock.price >= 0
const isBookable = stock => stock.isBookable
const isAvailable = stock => stock.available === null || stock.available > 0

const getPriceRangeFromStocks = stocks => {
  if (!stocks || !Array.isArray(stocks)) return []

  const pricesForAvailableStocks = stocks
    .filter(stock => hasPrice(stock) && isBookable(stock) && isAvailable(stock))
    .map(stock => stock.price)

  if (pricesForAvailableStocks.length === 0) return []

  const minimum_price = Math.min(...pricesForAvailableStocks)
  const maximum_price = Math.max(...pricesForAvailableStocks)

  return unique([minimum_price, maximum_price])
}

export default getPriceRangeFromStocks
