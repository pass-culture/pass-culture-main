import endOfDay from 'date-fns/endOfDay'
import isEqual from 'date-fns/isEqual'
import isSameDay from 'date-fns/isSameDay'
import startOfDay from 'date-fns/startOfDay'
import startOfMinute from 'date-fns/startOfMinute'

import { toISOStringWithoutMilliseconds } from 'utils/date'
import {
  getLocalDepartementDateTimeFromUtc,
  getUtcDateTimeFromLocalDepartement,
} from 'utils/timezone'

const buildBeginningDatetime = (beginningDateIsoString, beginningTimeIsoString) => {
  if (beginningDateIsoString === '' || beginningTimeIsoString === '') {
    return ''
  }

  const beginningDate = beginningDateIsoString.split('T')[0]
  const beginningTime = beginningTimeIsoString.split('T')[1].replace(/\.\d{3}/, '')
  return `${beginningDate}T${beginningTime}`
}

const getBookingLimitDatetimeForEvent = (stock, beginningDatetimeIsoString, departementCode) => {
  if (stock.bookingLimitDatetime === '') {
    return beginningDatetimeIsoString
  }
  const bookingLimitLocalDatetime = getLocalDepartementDateTimeFromUtc(
    stock.bookingLimitDatetime,
    departementCode
  )
  const beginningLocalDatetime = getLocalDepartementDateTimeFromUtc(
    beginningDatetimeIsoString,
    departementCode
  )
  if (isSameDay(bookingLimitLocalDatetime, beginningLocalDatetime)) {
    return beginningDatetimeIsoString
  } else {
    const endOfBookingLimitDayUtcDatetime = getUtcDateTimeFromLocalDepartement(
      endOfDay(bookingLimitLocalDatetime),
      departementCode
    )
    return toISOStringWithoutMilliseconds(endOfBookingLimitDayUtcDatetime)
  }
}

const getBookingLimitDatetimeForThing = (stock, departementCode) => {
  if (!stock.bookingLimitDatetime) {
    return null
  }
  const bookingLimitLocalDatetime = getLocalDepartementDateTimeFromUtc(
    stock.bookingLimitDatetime,
    departementCode
  )
  const endOfBookingLimitDayUtcDatetime = getUtcDateTimeFromLocalDepartement(
    endOfDay(bookingLimitLocalDatetime),
    departementCode
  )
  return toISOStringWithoutMilliseconds(endOfBookingLimitDayUtcDatetime)
}

export const createStockPayload = (stock, isEvent, departementCode) => {
  let payload = {
    price: stock.price ? stock.price : 0,
    quantity: stock.quantity ? stock.quantity : null,
  }
  if (isEvent) {
    payload.beginningDatetime = buildBeginningDatetime(stock.beginningDate, stock.beginningTime)
    payload.bookingLimitDatetime = getBookingLimitDatetimeForEvent(
      stock,
      payload.beginningDatetime,
      departementCode
    )
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
    isEqual(
      startOfMinute(new Date(originalStock.beginningDatetime)),
      startOfMinute(new Date(updatedStock.beginningDatetime))
    ) &&
    isEqual(
      startOfDay(new Date(originalStock.bookingLimitDatetime)),
      startOfDay(new Date(updatedStock.bookingLimitDatetime))
    ) &&
    originalStock.price === updatedStock.price &&
    originalStock.quantity === updatedStock.quantity
  )
}

export const formatAndSortStocks = stocks => {
  return stocks
    .map(stock => ({ ...stock, key: stock.id }))
    .sort(
      (stock1, stock2) =>
        new Date(stock2.beginningDatetime).getTime() - new Date(stock1.beginningDatetime).getTime()
    )
}
