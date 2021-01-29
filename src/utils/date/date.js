import moment from 'moment'
import 'moment-timezone'
import 'moment/locale/fr'

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
  return moment(dateString).tz(getTimezone(departementCode)).format('YYYY-MM-DD HH:mm:ss')
}

export const humanizeDate = (date, timezone) =>
  capitalize(moment(date).tz(timezone).format('dddd DD/MM/YYYY à H:mm'))

export const formatSearchResultDate = (departmentCode, allDatesInSeconds = []) => {
  const dates = allDatesInSeconds
    .map(seconds => new Date(MILLISECONDS_IN_A_SECOND * seconds))
    .filter(date => date > new Date())
    .sort()

  if (dates.length === 0) return null

  const timeZone = getTimezone(departmentCode)

  const numberOfBookableDates = dates.length
  const firstBookableDate = dates[0]
  const lastBookableDate = dates[numberOfBookableDates - 1]

  const day = firstBookableDate.toLocaleString(LOCALE_FRANCE, { timeZone, day: '2-digit' })
  const month = firstBookableDate.toLocaleString(LOCALE_FRANCE, { timeZone, month: 'long' })

  const bookableDatesAreOnTheSameDay = firstBookableDate.getDate() === lastBookableDate.getDate()
  const onlyOneBookableDate = numberOfBookableDates === 1
  if (bookableDatesAreOnTheSameDay || onlyOneBookableDate) {
    const hoursMinutes = firstBookableDate.toLocaleString(LOCALE_FRANCE, {
      timeZone,
      hour: '2-digit',
      minute: '2-digit',
    })

    const weekDay = firstBookableDate.toLocaleString(LOCALE_FRANCE, { timeZone, weekday: 'long' })
    const capitalizedWeekDay = weekDay.charAt(0).toUpperCase() + weekDay.slice(1)

    return `${capitalizedWeekDay} ${day} ${month} ${hoursMinutes}`
  }

  return `À partir du ${day} ${month}`
}
