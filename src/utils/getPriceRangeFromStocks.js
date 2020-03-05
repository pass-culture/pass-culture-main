const unique = array => array.filter((value, index, array) => index === array.indexOf(value))
const isBookable = stock => stock.isBookable

const getPriceRangeFromStocks = stocks => {
  if (!stocks || !Array.isArray(stocks)) return []

  const pricesForAvailableStocks = stocks
    .filter(stock => isBookable(stock))
    .map(stock => stock.price)

  if (pricesForAvailableStocks.length === 0) return []

  const minimum_price = Math.min(...pricesForAvailableStocks)
  const maximum_price = Math.max(...pricesForAvailableStocks)

  return unique([minimum_price, maximum_price])
}

export default getPriceRangeFromStocks
