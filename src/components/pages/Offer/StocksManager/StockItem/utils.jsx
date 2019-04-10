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

export function getDisplayedPrice(value, readOnly) {
  if (value === 0) {
    if (readOnly) {
      return 'Gratuit'
    }
    return 0
  }
  if (readOnly) {
    let floatValue = value
    if (value && String(value).includes(FLOATSEP)) {
      floatValue = parseFloat(value.replace(/,/, '.')).toFixed(2)
    }
    let floatValueString = `${floatValue} €`
    if (FLOATSEP === ',') {
      floatValueString = floatValueString.replace('.', ',')
    }
    return floatValueString
  }

  if (value === ' ') {
    return 0
  }

  return value
}

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

export function getDatetimeTwoDaysBefore(datetime) {
  return moment(datetime)
    .subtract(2, 'day')
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
