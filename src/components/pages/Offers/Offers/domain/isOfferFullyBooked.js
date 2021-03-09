export const isOfferFullyBooked = stocks => {
  const futureStocks = stocks.filter(stock => stock.hasBookingLimitDatetimePassed === false)
  const hasUnlimitedStock = futureStocks.some(stock => stock.remainingQuantity === 'unlimited')

  if (hasUnlimitedStock) {
    return false
  }

  return futureStocks.every(stock => stock.remainingQuantity <= 0)
}
