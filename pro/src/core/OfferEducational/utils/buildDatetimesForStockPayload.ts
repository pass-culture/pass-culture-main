import { endOfDay, isSameDay } from 'date-fns'

import { buildDateTime } from 'screens/OfferIndividual/StocksEventEdition/adapters/serializers'

import {
  isDateValid,
  toISOStringWithoutMilliseconds,
} from '../../../utils/date'
import { getUtcDateTimeFromLocalDepartement } from '../../../utils/timezone'

export const getBookingLimitDatetime = (
  bookingLimitDatetime: string,
  beginningDateTimeInDepartmentTimezone: Date
): Date => {
  if (!isDateValid(bookingLimitDatetime)) {
    return beginningDateTimeInDepartmentTimezone
  }
  if (
    isSameDay(
      new Date(bookingLimitDatetime),
      beginningDateTimeInDepartmentTimezone
    )
  ) {
    return beginningDateTimeInDepartmentTimezone
  } else {
    return endOfDay(new Date(bookingLimitDatetime))
  }
}

export const buildBeginningDatetimeForStockPayload = (
  eventDate: string,
  eventTime: string,
  departmentCode: string
): string => {
  const beginningDateTimeInUserTimezone = buildDateTime(eventDate, eventTime)
  const beginningDateTimeInUTCTimezone = getUtcDateTimeFromLocalDepartement(
    beginningDateTimeInUserTimezone,
    departmentCode
  )
  return toISOStringWithoutMilliseconds(beginningDateTimeInUTCTimezone)
}

export const buildBookingLimitDatetimeForStockPayload = (
  eventDate: string,
  eventTime: string,
  bookingLimitDatetime: string,
  departmentCode: string
): string => {
  const beginningDateTimeInUserTimezone = buildDateTime(eventDate, eventTime)
  const bookingLimitDatetimeUtc = getUtcDateTimeFromLocalDepartement(
    getBookingLimitDatetime(
      bookingLimitDatetime,
      beginningDateTimeInUserTimezone
    ),
    departmentCode
  )
  return toISOStringWithoutMilliseconds(bookingLimitDatetimeUtc)
}
