import moment from 'moment'
import 'moment-timezone'

import { MILLISECONDS_IN_A_SECOND } from '../../components/pages/search/utils/date/time'
import { capitalize } from '../react-form-utils/functions'
import { getTimezone } from '../timezone'

export const LOCALE_FRANCE = 'fr-FR'
export const FULL_MONTH_IN_LETTERS = { month: 'long' }
export const MONTH_IN_NUMBER = { month: 'numeric' }
export const PASS_CULTURE_YEARS_VALIDITY = 2
export const YEAR_IN_NUMBER = { year: 'numeric' }

const formatDate = (date, timeZone) => {
  const options = {
    timeZone,
  }
  return `${date.toLocaleDateString(LOCALE_FRANCE, options)}`
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

  const numberOfBookableDates = dates.length
  let firstBookableDate = new Date(dates[0] * MILLISECONDS_IN_A_SECOND)
  let lastBookableDate = new Date(dates[numberOfBookableDates - 1] * MILLISECONDS_IN_A_SECOND)

  const day = firstBookableDate.toLocaleString(LOCALE_FRANCE, { timezone, day: '2-digit' })
  const month = firstBookableDate.toLocaleString(LOCALE_FRANCE, { timezone, month: 'long' })

  const bookableDatesAreOnTheSameDay = firstBookableDate.getDate() === lastBookableDate.getDate()
  const onlyOneBookableDate = numberOfBookableDates === 1
  if (bookableDatesAreOnTheSameDay || onlyOneBookableDate) {
    const hours = firstBookableDate.getHours()
    const minutes = firstBookableDate.getMinutes()
    const hoursWithLeadingZero = hours < 10 ? '0' + hours : hours
    const minutesWithLeadingZero = minutes < 10 ? '0' + minutes : minutes
    const weekDay = firstBookableDate.toLocaleString(LOCALE_FRANCE, { timezone, weekday: 'long' })

    const capitalizedWeekDay = weekDay.charAt(0).toUpperCase() + weekDay.slice(1)
    return `${capitalizedWeekDay} ${day} ${month} ${hoursWithLeadingZero}:${minutesWithLeadingZero}`
  }

  return `A partir du ${day} ${month}`
}
