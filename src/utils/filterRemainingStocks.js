const filterRemainingStocks = stocks => {
  return stocks.filter(
    stock =>
      stock.remainingQuantityOrUnlimited &&
      (stock.remainingQuantityOrUnlimited > 0 || stock.remainingQuantityOrUnlimited === 'unlimited')
  )
}

export default filterRemainingStocks
