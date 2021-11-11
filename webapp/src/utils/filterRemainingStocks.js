const filterRemainingStocks = stocks => {
  return stocks.filter(
    stock =>
      stock.remainingQuantity &&
      (stock.remainingQuantity > 0 || stock.remainingQuantity === 'unlimited')
  )
}

export default filterRemainingStocks
