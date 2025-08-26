import { isValid } from 'date-fns'
import { fr } from 'date-fns/locale'
import { format } from 'date-fns-tz'

import type { WeekdayOpeningHoursTimespans } from '@/apiClient/v1'

const FORMAT_ISO = "yyyy-MM-dd'T'HH:mm:ssX"
export const FORMAT_ISO_DATE_ONLY = 'yyyy-MM-dd'
export const FORMAT_DD_MM_YYYY_HH_mm = 'dd/MM/yyyy HH:mm'
export const FORMAT_DD_MM_YYYY = 'dd/MM/yyyy'
export const FORMAT_DD_MMMM_YYYY = 'dd MMMM yyyy'
export const FORMAT_HH_mm = 'HH:mm'

export const buildDateTime = (date: string, time: string) => {
  const hoursAndMinutes = time.split(':')
  if (!isDateValid(date) || hoursAndMinutes.length < 2) {
    throw Error('La date ou l’heure est invalide')
  }
  const [hours, minutes] = hoursAndMinutes
  const [year, month, day] = date.split('-')

  // new Date(year, month, day, hours, minutes)
  return new Date(
    parseInt(year, 10),
    parseInt(month, 10) - 1,
    parseInt(day, 10),
    parseInt(hours, 10),
    parseInt(minutes, 10)
  )
}

export const formatDateTimeParts = (
  date?: string | null
): { date: string; time: string } => {
  const formattedDate = isDateValid(date)
    ? format(new Date(date), FORMAT_DD_MM_YYYY)
    : ''
  const formattedTime = isDateValid(date)
    ? format(new Date(date), FORMAT_HH_mm)
    : ''

  return { date: formattedDate, time: formattedTime }
}

export const removeTime = (date: Date): Date => {
  date.setHours(0)
  date.setMinutes(0)
  date.setSeconds(0)
  date.setMilliseconds(0)
  return date
}

export const isDateValid = (
  date?: Date | null | string
): date is Date | string =>
  isValid(typeof date === 'string' ? new Date(date) : date)

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
  if (!isValid(new Date(dateIsoString))) {
    return null
  }
  const noTimeZoneDate = toDateStrippedOfTimezone(dateIsoString)
  return format(noTimeZoneDate, FORMAT_DD_MMMM_YYYY, { locale: fr })
}

export function getDateTimeToFrenchText(
  date: Date,
  options: Intl.DateTimeFormatOptions = {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  }
): string {
  return Intl.DateTimeFormat('fr-FR', options).format(date)
}

export function getRangeToFrenchText(
  from: Date,
  to: Date,
  shouldDisplayTime: boolean
): string {
  //  The time displayed will be the one taken from the first date
  const isSameYear = from.getFullYear() === to.getFullYear()
  const isSameMonth = isSameYear && from.getMonth() === to.getMonth()
  const isSameDay = isSameYear && isSameMonth && from.getDate() === to.getDate()

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

export function getDelayToFrenchText(delay: number): string {
  const timeInHour = delay / 60 / 60

  if (timeInHour < 1) {
    return `${timeInHour * 60} minutes`
  } else if (timeInHour === 1) {
    return `${timeInHour} heure`
  } else if (timeInHour > 48) {
    return `${timeInHour / 24} jours`
  }
  return `${timeInHour} heures`
}

export const toISOStringWithoutMilliseconds = (date: Date) => {
  return date.toISOString().replace(/\.\d{3}/, '')
}

export const getYearMonthDay = (date: string) => {
  const [year, month, day] = date.split('-')
  return [parseInt(year), parseInt(month) - 1, parseInt(day)]
}

export function formatShortDateForInput(date: Date) {
  //  sv-se is similar to ISO 8601 for the short date format, which is used in HTML Input dates
  //  The output format is yyyy-MM-dd
  return new Intl.DateTimeFormat('sv-se').format(date)
}

export function formatTimeForInput(date: Date) {
  //  sv-se is similar to ISO 8601 for the time format, which is used in HTML Input dates
  //  The output format is HH:mm
  return new Intl.DateTimeFormat('sv-se', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

export function mapDayToFrench(
  day: string
):
  | 'Lundi'
  | 'Mardi'
  | 'Mercredi'
  | 'Jeudi'
  | 'Vendredi'
  | 'Samedi'
  | 'Dimanche' {
  switch (day.toUpperCase()) {
    case 'MONDAY':
      return 'Lundi'
    case 'TUESDAY':
      return 'Mardi'
    case 'WEDNESDAY':
      return 'Mercredi'
    case 'THURSDAY':
      return 'Jeudi'
    case 'FRIDAY':
      return 'Vendredi'
    case 'SATURDAY':
      return 'Samedi'
    case 'SUNDAY':
      return 'Dimanche'
    default:
      return 'Dimanche'
  }
}

export const OPENING_HOURS_DAYS: (keyof WeekdayOpeningHoursTimespans)[] = [
  'MONDAY',
  'TUESDAY',
  'WEDNESDAY',
  'THURSDAY',
  'FRIDAY',
  'SATURDAY',
  'SUNDAY',
]
