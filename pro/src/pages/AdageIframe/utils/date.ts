import { format } from 'date-fns-tz'

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
