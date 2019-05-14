import moment from 'moment'

export const getRemainingStocksCount = (available, bookings) => {
  if (!available && available !== 0) {
    return 'Illimité'
  }

  const validBookings = bookings.filter(
    booking => booking.isCancelled === false
  )

  return available - validBookings.length
}

export const FLOATSEP = ','

export const BOOKING_LIMIT_DATETIME_HOURS = 23
export const BOOKING_LIMIT_DATETIME_MINUTES = 59

export function getDatetimeOneDayAfter(datetime) {
  return moment(datetime)
    .add(1, 'day')
    .toISOString()
}

export function getDatetimeOneHourAfter(datetime) {
  return moment(datetime)
    .add(1, 'hour')
    .toISOString()
}

export function getDatetimeTwoDaysBeforeAtSpecificHoursAndMinutes(
  datetime,
  hours,
  minutes
) {
  return moment(datetime)
    .subtract(2, 'day')
    .hours(hours)
    .minutes(minutes)
    .toISOString()
}

export function errorKeyToFrenchKey(errorKey) {
  switch (errorKey) {
    case 'available':
      return 'Places'
    case 'beginningDatetime':
      return 'Date de début'
    case 'bookingLimitDatetime':
      return 'Date de réservation'
    case 'endDatetime':
      return 'Date de fin'
    case 'price':
      return 'Prix'
    default:
      return errorKey
  }
}

export const createFormatAvailable = readOnly => value => {
  if (value === null) {
    return 'Illimité'
  }
  return value
}

export const createFormatPrice = readOnly => value => {
  if (value === '' || (readOnly && value === 0)) {
    return 'Gratuit'
  }
  return value
}
