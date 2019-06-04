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

export const BOOKING_LIMIT_DATETIME_HOURS = 23
export const BOOKING_LIMIT_DATETIME_MINUTES = 59
export const DEFAULT_BEGINNING_DATE_TIME_HOURS = 20
export const DEFAULT_BEGINNING_DATE_TIME_MINUTES = 0

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

export function getDatetimeAtSpecificHoursAndMinutes(
  datetime,
  hours,
  minutes,
  timezone
) {
  let datetimeMoment = moment(datetime)
  if (timezone) {
    datetimeMoment = datetimeMoment.tz(timezone)
  }
  return datetimeMoment
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

export const createFormatAvailable = () => value => {
  if (value === null) {
    return 'Illimité'
  }
  return value
}

export const formatPrice = readOnly => value => {
  if (readOnly && (value === null || value === 0 || value === '')) {
    return 'Gratuit'
  }

  if (typeof value === 'string') {
    if (value.includes(',')) {
      return value.replace(',', '.')
    }
  }

  return value
}
