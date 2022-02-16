import { format } from 'date-fns-tz'

import { formatLocalTimeDateString } from './timezone'

export const FORMAT_ISO = "yyyy-MM-dd'T'HH:mm:ssX"
export const FORMAT_ISO_DATE_ONLY = 'yyyy-MM-dd'
export const FORMAT_DD_MM_YYYY_HH_mm = 'dd/MM/yyyy HH:mm'
export const FORMAT_DD_MM_YYYY = 'dd/MM/yyyy'
export const FORMAT_HH_mm = 'HH:mm'

export const getToday = (): Date => new Date()

export const formatBrowserTimezonedDateAsUTC = (
  date: Date,
  dateFormat = FORMAT_ISO
): string => {
  return format(date, dateFormat, { timeZone: 'UTC' })
}

export const toDateStrippedOfTimezone = (dateIsoString: string): Date => {
  const dateIsoStringWithoutTimezone = dateIsoString.replace(
    /[+-][0-2]\d:[0-5]\d|Z/,
    ''
  )
  return new Date(dateIsoStringWithoutTimezone)
}

export const toISOStringWithoutMilliseconds = (date: Date): string => {
  return date.toISOString().replace(/\.\d{3}/, '')
}

const extractDepartmentCode = (venuePostalCode: string): string => {
  const departmentNumberBase: number = parseInt(venuePostalCode.slice(0, 2))
  if (departmentNumberBase > 95) {
    return venuePostalCode.slice(0, 3)
  } else {
    return venuePostalCode.slice(0, 2)
  }
}

export const formatDatetimeToPostalCodeTimezone = (
  datetime: Date,
  venuePostalCode: string,
  dateFormat: string
): string => {
  const departmentCode = extractDepartmentCode(venuePostalCode)
  const dateUTC = new Date(datetime)
  const dateUTCISOString = toISOStringWithoutMilliseconds(dateUTC)
  const localDate = formatLocalTimeDateString(
    dateUTCISOString,
    departmentCode,
    dateFormat
  )

  return localDate
}
