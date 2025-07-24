import { isDateValid, toISOStringWithoutMilliseconds } from 'commons/utils/date'
import { getUtcDateTimeFromLocalDepartement } from 'commons/utils/timezone'

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
