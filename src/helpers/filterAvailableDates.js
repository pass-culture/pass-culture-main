import moment from 'moment'

export const filterAvailableDates = (stocks, limit = false) => {
  const now = limit || moment()
  // tuto n'a pas de stock
  const filtered = (stocks || []).filter(item => {
    // item.bookingLimitDatetime est ISOString
    const bookingLimit = moment(item.bookingLimitDatetime)
    return bookingLimit.isAfter(now, 'day')
  })
  return filtered
}

export default filterAvailableDates
