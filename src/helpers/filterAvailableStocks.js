import moment from 'moment'

export const filterAvailableStocks = (stocks, limit = false) => {
  const now = limit || moment()
  // tuto n'a pas de stock
  const filtered = (stocks || []).filter(item => {
    // item.bookingLimitDatetime est ISOString
    if (!item.bookingLimitDatetime)
        return true
    const bookingLimit = moment(item.bookingLimitDatetime)
    return !item.bookingLimitDatetime || bookingLimit.isAfter(now, 'day')
  })
  return filtered
}

export default filterAvailableStocks
