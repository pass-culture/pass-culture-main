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

export const isDateValid = (
  date?: Date | null | string
): date is Date | string => {
  if (date === null || date === undefined || date === '') {
    return false
  }
  const dateAsDate = typeof date === 'string' ? new Date(date) : date
  return dateAsDate instanceof Date && !isNaN(dateAsDate.getTime())
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

function getDateTimeToFrenchText(
  date: Date,
  options: Intl.DateTimeFormatOptions = {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  }
): string {
  return Intl.DateTimeFormat('fr-FR', options).format(date)
}

export function getRangeToFrenchText(from: Date, to: Date): string {
  //  The time displayed will be the one taken from the first date

  const isSameYear = from.getFullYear() === to.getFullYear()
  const isSameMonth = isSameYear && from.getMonth() === to.getMonth()
  const isSameDay = isSameYear && isSameMonth && from.getDate() === to.getDate()

  const shouldDisplayTime = from.getHours() !== 0 || from.getMinutes() !== 0

  const timeToFrenchText = getDateTimeToFrenchText(from, {
    hour: '2-digit',
    minute: from.getMinutes() === 0 ? undefined : '2-digit',
  })
    .replace(':', 'h')
    .replace(' ', '')

  const formattedTime = shouldDisplayTime ? ` à ${timeToFrenchText}` : ''

  if (isSameDay) {
    return `Le ${getDateTimeToFrenchText(from, {
      dateStyle: 'full',
    })}${formattedTime}`
  }

  if (isSameYear) {
    return `Du ${getDateTimeToFrenchText(from, {
      day: '2-digit',
      month: 'long',
    })} au ${getDateTimeToFrenchText(to)}${formattedTime}`
  }

  return `Du ${getDateTimeToFrenchText(from)} au ${getDateTimeToFrenchText(
    to
  )}${formattedTime}`
}

export const toISOStringWithoutMilliseconds = (date: Date) => {
  return date.toISOString().replace(/\.\d{3}/, '')
}

export const getYearMonthDay = (date: string) => {
  const [year, month, day] = date.split('-')
  return [parseInt(year), parseInt(month) - 1, parseInt(day)]
}
