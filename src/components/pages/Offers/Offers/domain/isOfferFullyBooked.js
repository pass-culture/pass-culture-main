export const isOfferFullyBooked = stocks => {
  const hasUnlimitedStock = stocks.some(stock => stock.remainingQuantity === 'unlimited')

  if (hasUnlimitedStock) {
    return false
  }

  return stocks.every(stock => stock.remainingQuantity <= 0)
}
