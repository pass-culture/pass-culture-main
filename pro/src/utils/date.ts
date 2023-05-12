import { fr } from 'date-fns/locale'
import { format } from 'date-fns-tz'

const FORMAT_ISO = "yyyy-MM-dd'T'HH:mm:ssX"
export const FORMAT_ISO_DATE_ONLY = 'yyyy-MM-dd'
export const FORMAT_DD_MM_YYYY_HH_mm = 'dd/MM/yyyy HH:mm'
export const FORMAT_DD_MM_YYYY = 'dd/MM/yyyy'
const FORMAT_DD_MMMM_YYYY = 'dd MMMM yyyy'
export const FORMAT_HH_mm = 'HH:mm'

export const removeTime = (date: Date): Date => {
  date.setHours(0)
  date.setMinutes(0)
  date.setSeconds(0)
  date.setMilliseconds(0)
  return date
}

export const getToday = () => new Date()

export const formatBrowserTimezonedDateAsUTC = (
  date: Date | number,
  dateFormat = FORMAT_ISO
) => {
  return format(date, dateFormat, { timeZone: 'UTC' })
}

export const toDateStrippedOfTimezone = (dateIsoString: string) => {
  const dateIsoStringWithoutTimezone = dateIsoString.replace(
    /[+-][0-2]\d:[0-5]\d|Z/,
    ''
  )
  return new Date(dateIsoStringWithoutTimezone)
}

export const getDateToFrenchText = (dateIsoString: string) => {
  const noTimeZoneDate = toDateStrippedOfTimezone(dateIsoString)
  return format(noTimeZoneDate, FORMAT_DD_MMMM_YYYY, { locale: fr })
}

export const toISOStringWithoutMilliseconds = (date: Date) => {
  return date.toISOString().replace(/\.\d{3}/, '')
}
