import moment from 'moment-timezone'

const buildBeginningDatetime = (beginningDate, beginningTime) => {
  if (beginningDate === '' || beginningTime === '') {
    return ''
  }
  const momentBeginningDate = moment(beginningDate)
  const momentBeginningTime = moment(beginningTime)

  momentBeginningDate.hours(momentBeginningTime.hours())
  momentBeginningDate.minutes(momentBeginningTime.minutes())

  return momentBeginningDate.utc().format()
}

const getBookingLimitDatetimeForEvent = (stock, beginningDatetime) => {
  const momentBookingLimitDatetime = moment(stock.bookingLimitDatetime)
  if (
    stock.bookingLimitDatetime === '' ||
    momentBookingLimitDatetime.isSame(beginningDatetime, 'day')
  ) {
    return beginningDatetime
  } else {
    return momentBookingLimitDatetime.utc().endOf('day').format()
  }
}

const getBookingLimitDatetimeForThing = stock => {
  if (stock.bookingLimitDatetime) {
    return moment(stock.bookingLimitDatetime).utc().endOf('day').format()
  }
  return null
}

export const createStockPayload = (stock, isEvent) => {
  let payload = {
    price: stock.price ? stock.price : 0,
    quantity: stock.quantity ? stock.quantity : null,
  }
  if (isEvent) {
    payload.beginningDatetime = buildBeginningDatetime(stock.beginningDate, stock.beginningTime)
    payload.bookingLimitDatetime = getBookingLimitDatetimeForEvent(stock, payload.beginningDatetime)
  } else {
    payload.bookingLimitDatetime = getBookingLimitDatetimeForThing(stock)
  }
  return payload
}

export const validateCreatedStock = stock => {
  let errors = {}

  if (stock.price < 0) {
    errors.price = 'Le prix doit être positif.'
  }

  if (stock.quantity < 0) {
    errors.quantity = 'La quantité doit être positive.'
  }

  if (stock.beginningDate === '') {
    errors.beginningDate = 'Ce champ est obligatoire.'
  }

  if (stock.beginningTime === '') {
    errors.beginningTime = 'Ce champ est obligatoire.'
  }

  return errors
}

export const validateUpdatedStock = stock => {
  let errors = validateCreatedStock(stock)

  const remainingQuantity = stock.quantity - stock.bookingsQuantity

  if (stock.quantity && remainingQuantity < 0) {
    const missingQuantityMessage = 'La quantité ne peut être inférieure au nombre de réservations.'
    if ('quantity' in Object.keys(errors)) {
      errors.quantity = errors.quantity.concat('\n', missingQuantityMessage)
    } else {
      errors.quantity = missingQuantityMessage
    }
  }

  return errors
}

export const hasStockBeenUpdated = (originalStock, updatedStock) => {
  if (updatedStock.beginningDate) {
    updatedStock.beginningDatetime = buildBeginningDatetime(
      updatedStock.beginningDate,
      updatedStock.beginningTime
    )
  }

  return !(
    moment(originalStock.beginningDatetime).isSame(updatedStock.beginningDatetime, 'minute') &&
    moment(originalStock.bookingLimitDatetime).isSame(updatedStock.bookingLimitDatetime, 'day') &&
    originalStock.price === updatedStock.price &&
    originalStock.quantity === updatedStock.quantity
  )
}

export const formatAndSortStocks = stocks => {
  return stocks
    .map(stock => ({ ...stock, key: stock.id }))
    .sort(
      (stock1, stock2) =>
        moment(stock2.beginningDatetime).unix() - moment(stock1.beginningDatetime).unix()
    )
}
