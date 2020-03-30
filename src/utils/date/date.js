import moment from 'moment'
import 'moment-timezone'

import { getTimezone } from '../timezone'
import { capitalize } from '../react-form-utils/functions'

const PASS_CULTURE_YEARS_VALIDITY = 2
const LOCALE = 'fr-FR'

const formatDate = (date, timeZone) => {
  const options = {
    timeZone,
  }

  return `${date.toLocaleDateString('fr-FR', options)}`
}

export const formatRecommendationDates = (departementCode, dateRange = []) => {
  if (dateRange.length === 0) return 'permanent'

  const timeZone = getTimezone(departementCode)
  const fromDate = new Date(dateRange[0])
  const toDate = new Date(dateRange[1])
  const fromFormated = formatDate(fromDate, timeZone)
  const toFormated = formatDate(toDate, timeZone)

  return `du ${fromFormated} au ${toFormated}`
}

export const computeEndValidityDate = date => {
  const options = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }
  date.setFullYear(date.getFullYear() + PASS_CULTURE_YEARS_VALIDITY)

  return `${date.toLocaleDateString('fr-FR', options)}`
}

export const dateStringPlusTimeZone = (dateString, departementCode) => {
  return moment(dateString)
    .tz(getTimezone(departementCode))
    .format('YYYY-MM-DD HH:mm:ss')
}

export const humanizeDate = (date, timezone) =>
  capitalize(
    moment(date)
      .tz(timezone)
      .format('dddd DD/MM/YYYY à H:mm')
  )

export const formatSearchResultDate = (departmentCode, dates = []) => {
  if (dates.length === 0) return null
  const timezone = getTimezone(departmentCode)
  let beginningDatetime = new Date(dates[0] * 1000)
  let endingDatetime = new Date(dates[1] * 1000)

  const day = beginningDatetime.toLocaleString(LOCALE, { timezone, day: '2-digit' })
  const month = beginningDatetime.toLocaleString(LOCALE, { timezone, month: 'long' })
  const weekDay = beginningDatetime.toLocaleString(LOCALE, { timezone, weekday: 'short' })

  if (beginningDatetime.getDate() === endingDatetime.getDate()) {
    const hours = beginningDatetime.getHours()
    const minutes = beginningDatetime.getMinutes()
    const hoursWithLeadingZero = hours < 10 ? '0' + hours : hours
    const minutesWithLeadingZero = minutes < 10 ? '0' + minutes : minutes
    const monthShortened = beginningDatetime.toLocaleString(LOCALE, { timezone, month: 'short' })

    return `${weekDay.toLowerCase()} ${day} ${monthShortened.toLowerCase()} ${hoursWithLeadingZero}:${minutesWithLeadingZero}`
  }
  return `A partir du ${day} ${month}`
}
