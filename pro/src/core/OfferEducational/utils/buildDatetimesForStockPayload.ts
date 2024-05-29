import { endOfDay, isSameDay } from 'date-fns'

import { buildDateTime } from 'screens/IndividualOffer/StocksEventEdition/serializers'

import {
  isDateValid,
  toISOStringWithoutMilliseconds,
} from '../../../utils/date'
import { getUtcDateTimeFromLocalDepartement } from '../../../utils/timezone'

const getBookingLimitDatetime = (
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

export const buildStartDatetimeForStockPayload = (
  startDatetime: string,
  eventTime: string,
  departmentCode: string
): string => {
  const startDatetimeInUserTimezone = buildDateTime(startDatetime, eventTime)
  const beginningDateTimeInUTCTimezone = getUtcDateTimeFromLocalDepartement(
    startDatetimeInUserTimezone,
    departmentCode
  )
  return toISOStringWithoutMilliseconds(beginningDateTimeInUTCTimezone)
}

export const buildEndDatetimeForStockPayload = (
  endDatetime: string,
  eventTime: string,
  departmentCode: string
) => {
  const endDatetimeInUserTimezone = buildDateTime(endDatetime, eventTime)
  const endDateTimeInUTCTimezone = getUtcDateTimeFromLocalDepartement(
    endDatetimeInUserTimezone,
    departmentCode
  )
  return toISOStringWithoutMilliseconds(endDateTimeInUTCTimezone)
}

export const buildBookingLimitDatetimeForStockPayload = (
  startDatetime: string,
  eventTime: string,
  bookingLimitDatetime: string,
  departmentCode: string
): string => {
  const beginningDateTimeInUserTimezone = buildDateTime(
    startDatetime,
    eventTime
  )
  const bookingLimitDatetimeUtc = getUtcDateTimeFromLocalDepartement(
    getBookingLimitDatetime(
      bookingLimitDatetime,
      beginningDateTimeInUserTimezone
    ),
    departmentCode
  )
  return toISOStringWithoutMilliseconds(bookingLimitDatetimeUtc)
}
