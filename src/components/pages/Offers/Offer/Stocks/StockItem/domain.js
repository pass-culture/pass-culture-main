import { endOfDay, isEqual, isSameDay, set, startOfDay, startOfMinute } from 'date-fns'

import { toISOStringWithoutMilliseconds } from 'utils/date'
import {
  getLocalDepartementDateTimeFromUtc,
  getUtcDateTimeFromLocalDepartement,
} from 'utils/timezone'

const EMPTY_STRING_VALUE = ''

const buildBeginningDatetime = (beginningDateIsoString, beginningTimeIsoString) => {
  if (beginningDateIsoString === null || beginningTimeIsoString === null) {
    return ''
  }
  return set(beginningDateIsoString, {
    hours: beginningTimeIsoString.getHours(),
    minutes: beginningTimeIsoString.getMinutes(),
  })
}

const getBookingLimitDatetimeForEvent = (stock, beginningDateTimeInDepartementTimezone) => {
  if (stock.bookingLimitDatetime === null) {
    return beginningDateTimeInDepartementTimezone
  }
  if (isSameDay(stock.bookingLimitDatetime, beginningDateTimeInDepartementTimezone)) {
    return beginningDateTimeInDepartementTimezone
  } else {
    return endOfDay(stock.bookingLimitDatetime)
  }
}

const getBookingLimitDatetimeForThing = (stock, departementCode) => {
  if (!stock.bookingLimitDatetime) {
    return null
  }
  const endOfBookingLimitDayUtcDatetime = getUtcDateTimeFromLocalDepartement(
    endOfDay(stock.bookingLimitDatetime),
    departementCode
  )
  return toISOStringWithoutMilliseconds(endOfBookingLimitDayUtcDatetime)
}

export const createStockPayload = (stock, isEvent, departementCode) => {
  let payload = {
    price: stock.price,
    quantity: stock.quantity ? stock.quantity : null,
  }
  if (isEvent) {
    const beginningDateTimeInDepartementTimezone = buildBeginningDatetime(
      stock.beginningDate,
      stock.beginningTime
    )
    const bookingLimitDatetime = getUtcDateTimeFromLocalDepartement(
      getBookingLimitDatetimeForEvent(stock, beginningDateTimeInDepartementTimezone),
      departementCode
    )
    const beginningDateTimeInUTCTimezone = getUtcDateTimeFromLocalDepartement(
      beginningDateTimeInDepartementTimezone,
      departementCode
    )
    payload.beginningDatetime = toISOStringWithoutMilliseconds(beginningDateTimeInUTCTimezone)
    payload.bookingLimitDatetime = toISOStringWithoutMilliseconds(bookingLimitDatetime)
  } else {
    payload.bookingLimitDatetime = getBookingLimitDatetimeForThing(stock, departementCode)
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

  if (stock.beginningDate === null) {
    errors.beginningDate = 'Ce champ est obligatoire.'
  }

  if (stock.beginningTime === null) {
    errors.beginningTime = 'Ce champ est obligatoire.'
  }

  if (stock.price === EMPTY_STRING_VALUE) {
    errors.price = 'Ce champ est obligatoire.'
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

const hasBeginningDateTimeBeenUpdated = (originalStock, updatedStock) => {
  if (updatedStock.beginningDate === null || updatedStock.beginningTime === null) {
    return true
  }

  const updatedBeginningDateTime = buildBeginningDatetime(
    updatedStock.beginningDate,
    updatedStock.beginningTime
  )
  return !isEqual(
    startOfMinute(originalStock.beginningDatetime),
    startOfMinute(updatedBeginningDateTime)
  )
}

export const hasStockBeenUpdated = (originalStock, updatedStock) => {
  let hasEventDateBeenUpdated = false
  const isEvent = Boolean(originalStock.beginningDatetime)
  if (isEvent) {
    hasEventDateBeenUpdated = hasBeginningDateTimeBeenUpdated(originalStock, updatedStock)
  }

  return (
    hasEventDateBeenUpdated ||
    !isEqual(
      startOfDay(originalStock.bookingLimitDatetime),
      startOfDay(updatedStock.bookingLimitDatetime)
    ) ||
    originalStock.price !== updatedStock.price ||
    originalStock.quantity !== updatedStock.quantity
  )
}

export const formatAndSortStocks = (stocks, departementCode) => {
  return stocks
    .map(stock => {
      const formattedStock = {
        ...stock,
        bookingLimitDatetime: getLocalDepartementDateTimeFromUtc(
          stock.bookingLimitDatetime,
          departementCode
        ),
        key: stock.id,
      }
      if (stock.beginningDatetime) {
        formattedStock.beginningDatetime = getLocalDepartementDateTimeFromUtc(
          stock.beginningDatetime,
          departementCode
        )
      }
      return formattedStock
    })
    .sort(
      (stock1, stock2) => new Date(stock2.beginningDatetime) - new Date(stock1.beginningDatetime)
    )
}
