import moment from 'moment'

// FIXME -> to be moved to constants
const DEFAULT_TIMEZONE = 'Europe/Paris'

export const filterAvailableDates = (
  stocks,
  tz = DEFAULT_TIMEZONE,
  limit = false
) => {
  const now = limit || moment()
  // tuto n'a pas de stock
  const filtered = (stocks || []).filter(item => {
    const date = moment(item.bookingLimitDatetime).tz(tz)
    return date.isAfter(now, 'day')
  })
  return filtered
}

export default filterAvailableDates
