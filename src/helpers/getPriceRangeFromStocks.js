import uniq from 'lodash.uniq'

const getPriceRangeFromStocks = stocks => {
  if (!stocks || !Array.isArray(stocks)) return []
  const filtered = stocks
    .filter(stock => stock.price || stock.price === 0)
    .filter(stock => stock.available === null || stock.available > 0)
    .map(stock => stock.price)
  return uniq(filtered)
}

export default getPriceRangeFromStocks
