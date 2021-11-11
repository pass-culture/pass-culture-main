const unique = array => array.filter((value, index, array) => index === array.indexOf(value))
const isBookable = stock => stock.isBookable

const getPriceRangeFromStocks = stocks => {
  if (!stocks || !Array.isArray(stocks)) return []

  const pricesForAvailableStocks = stocks
    .filter(stock => isBookable(stock))
    .map(stock => stock.price)

  if (pricesForAvailableStocks.length === 0) return []

  const minimumPrice = Math.min(...pricesForAvailableStocks)
  const maximumPrice = Math.max(...pricesForAvailableStocks)

  return unique([minimumPrice, maximumPrice])
}

export default getPriceRangeFromStocks
