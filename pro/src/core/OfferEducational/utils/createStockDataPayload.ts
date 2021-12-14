import { endOfDay, isSameDay, set } from 'date-fns'

import { toISOStringWithoutMilliseconds } from 'utils/date'
import { getUtcDateTimeFromLocalDepartement } from 'utils/timezone'

import { OfferEducationalStockFormValues, StockPayload } from '..'

const buildBeginningDatetime = (
  beginningDateIsoString: Date,
  beginningTimeIsoString: Date
): Date =>
  set(beginningDateIsoString, {
    hours: beginningTimeIsoString.getHours(),
    minutes: beginningTimeIsoString.getMinutes(),
  })

const getBookingLimitDatetime = (
  values: OfferEducationalStockFormValues,
  beginningDateTimeInDepartementTimezone: Date
): Date => {
  if (!values.bookingLimitDatetime) {
    return beginningDateTimeInDepartementTimezone
  }
  if (
    isSameDay(
      new Date(values.bookingLimitDatetime),
      beginningDateTimeInDepartementTimezone
    )
  ) {
    return beginningDateTimeInDepartementTimezone
  } else {
    return endOfDay(new Date(values.bookingLimitDatetime))
  }
}

export const createStockDataPayload = (
  values: OfferEducationalStockFormValues,
  departementCode: string
): StockPayload => {
  if (
    !values.eventDate ||
    !values.eventTime ||
    !values.numberOfPlaces ||
    !values.totalPrice
  ) {
    throw Error('Missing required values')
  }
  const beginningDateTimeInDepartementTimezone = buildBeginningDatetime(
    values.eventDate,
    values.eventTime
  )
  const bookingLimitDatetime = getUtcDateTimeFromLocalDepartement(
    getBookingLimitDatetime(values, beginningDateTimeInDepartementTimezone),
    departementCode
  )
  const beginningDateTimeInUTCTimezone = getUtcDateTimeFromLocalDepartement(
    beginningDateTimeInDepartementTimezone,
    departementCode
  )
  return {
    beginningDatetime: toISOStringWithoutMilliseconds(
      beginningDateTimeInUTCTimezone
    ),
    bookingLimitDatetime: toISOStringWithoutMilliseconds(bookingLimitDatetime),
    totalPrice: values.totalPrice,
    numberOfTickets: values.numberOfPlaces,
  }
}
