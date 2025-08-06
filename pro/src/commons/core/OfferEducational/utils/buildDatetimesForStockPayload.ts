import { endOfDay, isSameDay } from 'date-fns'

import {
  isDateValid,
  toISOStringWithoutMilliseconds,
} from '@/commons/utils/date'
import { getUtcDateTimeFromLocalDepartement } from '@/commons/utils/timezone'
import { buildDateTime } from '@/components/IndividualOffer/StocksEventEdition/serializers'

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
