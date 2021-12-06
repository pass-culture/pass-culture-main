import { endOfDay, isSameDay, set } from 'date-fns'

import { OfferEducationalStockFormValues } from 'core/OfferEducationalStock/types'
import { toISOStringWithoutMilliseconds } from 'utils/date'
import { getUtcDateTimeFromLocalDepartement } from 'utils/timezone'

import { StockCreationPayload } from '../../types'

const buildBeginningDatetime = (
  beginningDateIsoString: Date,
  beginningTimeIsoString: Date
): Date => {
  if (beginningDateIsoString === null || beginningTimeIsoString === null) {
    throw Error('Missing date or time')
  }
  return set(beginningDateIsoString, {
    hours: beginningTimeIsoString.getHours(),
    minutes: beginningTimeIsoString.getMinutes(),
  })
}

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

export const createStockPayload = (
  offerId: string,
  values: OfferEducationalStockFormValues,
  departementCode: string
): StockCreationPayload => {
  const beginningDateTimeInDepartementTimezone = buildBeginningDatetime(
    new Date(values.eventDate),
    new Date(values.eventTime)
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
    offerId: offerId,
    beginningDatetime: toISOStringWithoutMilliseconds(
      beginningDateTimeInUTCTimezone
    ),
    bookingLimitDatetime: toISOStringWithoutMilliseconds(bookingLimitDatetime),
    totalPrice: values.totalPrice,
    numberOfTickets: values.numberOfPlaces,
  }
}
