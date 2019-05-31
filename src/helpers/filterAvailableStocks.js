import moment from 'moment'

const checkIfStockBookingLimitDatetimeIsAfter = now => stockItem => {
  if (!stockItem.bookingLimitDatetime) return true

  return moment(stockItem.bookingLimitDatetime).isAfter(now)
}

const filterAvailableStocks = stocks => {
  const isValid = stocks && Array.isArray(stocks)
  if (!isValid) return []

  const now = moment()
  return stocks
    .filter(stockItem => stockItem !== null)
    .filter(checkIfStockBookingLimitDatetimeIsAfter(now))
}

export default filterAvailableStocks
