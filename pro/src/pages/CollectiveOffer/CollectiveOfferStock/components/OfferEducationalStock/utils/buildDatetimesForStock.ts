import { endOfDay, isSameDay } from 'date-fns'

import {
  buildDateTime,
  isDateValid,
  toISOStringWithoutMilliseconds,
} from '@/commons/utils/date'
import { getUtcDateTimeFromLocalDepartement } from '@/commons/utils/timezone'

import type {
  CollectiveStockDatetimes,
  CollectiveStockFormDates,
} from '../types'

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

const buildDatetimeForStockPayload = (
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

const buildBookingLimitDatetimeForStockPayload = (
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

export const buildDatetimesForStock = (
  { startDate, endDate, eventTime, bookingLimitDate }: CollectiveStockFormDates,
  departmentCode: string
): CollectiveStockDatetimes => {
  return {
    startDatetime: buildDatetimeForStockPayload(
      startDate,
      eventTime,
      departmentCode
    ),
    endDatetime: buildDatetimeForStockPayload(
      endDate,
      eventTime,
      departmentCode
    ),
    bookingLimitDatetime: buildBookingLimitDatetimeForStockPayload(
      startDate,
      eventTime,
      bookingLimitDate,
      departmentCode
    ),
  }
}
