import moment from 'moment'

const filterAvailableStocks = stocks => {
  const isvalid = stocks && Array.isArray(stocks)
  if (!isvalid) return []
  const now = moment()
  // tuto n'a pas de stock
  const filtered = stocks
    .filter(item => item)
    .filter(item => {
      // item.bookingLimitDatetime est ISOString
      if (!item.bookingLimitDatetime) return true
      const bookingLimit = moment(item.bookingLimitDatetime)
      return bookingLimit.isAfter(now)
    })
  return filtered
}

export default filterAvailableStocks
