import { endOfDay, isSameDay } from 'date-fns'

import { buildDateTime } from 'screens/IndividualOffer/StocksEventEdition/serializers'

import {
  isDateValid,
  toISOStringWithoutMilliseconds,
} from '../../../utils/date'
import { getUtcDateTimeFromLocalDepartement } from '../../../utils/timezone'

const getBookingLimitDatetime = (
  bookingLimitDatetime: string,
  startDateTimeInUserTimezone: Date
): Date => {
  if (!isDateValid(bookingLimitDatetime)) {
    return startDateTimeInUserTimezone
  }
  if (isSameDay(new Date(bookingLimitDatetime), startDateTimeInUserTimezone)) {
    return startDateTimeInUserTimezone
  }
  return endOfDay(new Date(bookingLimitDatetime))
}

export const buildDatetimeForStockPayload = (
  datetime: string,
  eventTime: string,
  departmentCode: string
): string => {
  const datetimeInUserTimezone = buildDateTime(datetime, eventTime)
  const dateTimeInUTCTimezone = getUtcDateTimeFromLocalDepartement(
    datetimeInUserTimezone,
    departmentCode
  )
  return toISOStringWithoutMilliseconds(dateTimeInUTCTimezone)
}

export const buildBookingLimitDatetimeForStockPayload = (
  startDatetime: string,
  eventTime: string,
  bookingLimitDatetime: string,
  departmentCode: string
): string => {
  const startDateTimeInUserTimezone = buildDateTime(startDatetime, eventTime)
  const bookingLimitDatetimeUtc = getUtcDateTimeFromLocalDepartement(
    getBookingLimitDatetime(bookingLimitDatetime, startDateTimeInUserTimezone),
    departmentCode
  )
  return toISOStringWithoutMilliseconds(bookingLimitDatetimeUtc)
}
