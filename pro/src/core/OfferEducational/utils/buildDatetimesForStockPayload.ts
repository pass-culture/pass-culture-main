import { endOfDay, isSameDay, set } from 'date-fns'

import { toISOStringWithoutMilliseconds } from '../../../utils/date'
import { getUtcDateTimeFromLocalDepartement } from '../../../utils/timezone'

export const buildBeginningDatetime = (
  beginningDateIsoString: Date,
  beginningTimeIsoString: Date
): Date =>
  set(beginningDateIsoString, {
    hours: beginningTimeIsoString.getHours(),
    minutes: beginningTimeIsoString.getMinutes(),
  })

export const getBookingLimitDatetime = (
  bookingLimitDatetime: Date | null,
  beginningDateTimeInDepartmentTimezone: Date
): Date => {
  if (!bookingLimitDatetime) {
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
  eventDate: Date,
  eventTime: Date,
  departmentCode: string
): string => {
  const beginningDateTimeInDepartmentTimezone = buildBeginningDatetime(
    eventDate,
    eventTime
  )
  const beginningDateTimeInUTCTimezone = getUtcDateTimeFromLocalDepartement(
    beginningDateTimeInDepartmentTimezone,
    departmentCode
  )
  return toISOStringWithoutMilliseconds(beginningDateTimeInUTCTimezone)
}

export const buildBookingLimitDatetimeForStockPayload = (
  eventDate: Date,
  eventTime: Date,
  bookingLimitDatetime: Date | null,
  departmentCode: string
): string => {
  const beginningDateTimeInDepartmentTimezone = buildBeginningDatetime(
    eventDate,
    eventTime
  )
  const bookingLimitDatetimeUtc = getUtcDateTimeFromLocalDepartement(
    getBookingLimitDatetime(
      bookingLimitDatetime,
      beginningDateTimeInDepartmentTimezone
    ),
    departmentCode
  )
  return toISOStringWithoutMilliseconds(bookingLimitDatetimeUtc)
}
