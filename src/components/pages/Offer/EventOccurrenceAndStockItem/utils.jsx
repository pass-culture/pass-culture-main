export const getRemaingStock = (availableStock, bookings) => {
  if (!availableStock && availableStock !== 0) {
    return 'Illimité'
  }
  const numbersbookings = bookings.length
  return availableStock - numbersbookings
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
