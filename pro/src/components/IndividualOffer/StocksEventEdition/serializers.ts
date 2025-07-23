import { endOfDay } from 'date-fns'

import {
  isDateValid,
  toISOStringWithoutMilliseconds
} from 'commons/utils/date'
import { getUtcDateTimeFromLocalDepartement } from 'commons/utils/timezone'

const serializeBookingLimitDatetime = (
  beginningDate: string,
  beginningTime: string,
  bookingLimitDatetime: string,
  departementCode?: string | null
) => {
  // If the bookingLimitDatetime is the same day as the start of the event
  // the bookingLimitDatetime should be set to beginningDate and beginningTime
  // ie : bookable until the event
  if (
    new Date(beginningDate).toDateString() ===
    new Date(bookingLimitDatetime).toDateString()
  ) {
    return serializeDateTimeToUTCFromLocalDepartment(
      beginningDate,
      beginningTime,
      departementCode
    )
  }
  const [year, month, day] = bookingLimitDatetime.split('-')
  const endOfBookingLimitDayUtcDatetime = getUtcDateTimeFromLocalDepartement(
    endOfDay(new Date(parseInt(year), parseInt(month) - 1, parseInt(day))),
    departementCode
  )
  return toISOStringWithoutMilliseconds(endOfBookingLimitDayUtcDatetime)
}

export const buildDateTime = (date: string, time: string) => {
  const hoursAndMinutes = time.split(':')
  if (!isDateValid(date) || hoursAndMinutes.length < 2) {
    throw Error('La date ou l’heure est invalide')
  }
  const [hours, minutes] = hoursAndMinutes
  const [year, month, day] = date.split('-')

  // new Date(year, month, day, hours, minutes)
  return new Date(
    parseInt(year),
    parseInt(month) - 1,
    parseInt(day),
    parseInt(hours),
    parseInt(minutes)
  )
}

export const serializeDateTimeToUTCFromLocalDepartment = (
  beginningDate: string,
  beginningTime: string,
  departementCode?: string | null
): string => {
  const beginningDateTimeInUserTimezone = buildDateTime(
    beginningDate,
    beginningTime
  )

  const beginningDateTimeInUTCTimezone = getUtcDateTimeFromLocalDepartement(
    beginningDateTimeInUserTimezone,
    departementCode
  )

  return toISOStringWithoutMilliseconds(beginningDateTimeInUTCTimezone)
}


