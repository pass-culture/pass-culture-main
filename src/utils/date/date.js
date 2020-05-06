import moment from 'moment'
import 'moment-timezone'
import { capitalize } from '../react-form-utils/functions'

import { getTimezone } from '../timezone'

export const FULL_MONTH_IN_LETTERS = { month: 'long' }
export const LOCALE_FRANCE = 'fr-FR'
export const MONTH_IN_NUMBER = { month: 'numeric' }
export const YEAR_IN_NUMBER = { year: 'numeric' }

const DAYS_IN_A_WEEK = 7
const MILLISECONDS_IN_A_DAY = 86400000
const MILLISECONDS_IN_A_MINUTE = 60000
const MILLISECONDS_IN_A_SECOND = 1000
const PASS_CULTURE_YEARS_VALIDITY = 2
const SATURDAY_INDEX_IN_A_WEEK = 6

const SUNDAY_INDEX_IN_A_WEEK = 0
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
export const computeEndValidityDate = date => {
  const options = {
    ...YEAR_IN_NUMBER,
    ...MONTH_IN_NUMBER,
    day: 'numeric',
  }

  date.setFullYear(date.getFullYear() + PASS_CULTURE_YEARS_VALIDITY)
  return `${date.toLocaleDateString(LOCALE_FRANCE, options)}`
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

export const getFirstTimestampForGivenDate = date => {
  const day = date.getDate()
  const month = date.getMonth()
  const year = date.getFullYear()
  return getTimestampFromDate(new Date(year, month, day, 0, 0, 0, 0))
}

export const getLastTimestampForGivenDate = date => {
  const day = date.getDate()
  const month = date.getMonth()
  const year = date.getFullYear()
  return getTimestampFromDate(new Date(year, month, day, 23, 59, 59, 0))
}

export const getLastTimestampOfTheWeekForGivenDate = date => {
  const dayOfTheWeek = date.getDay()
  if (dayOfTheWeek === SUNDAY_INDEX_IN_A_WEEK) return getLastTimestampForGivenDate(date)
  const daysUntilSunday = DAYS_IN_A_WEEK - dayOfTheWeek
  const dateOfNextSunday = date.getTime() + MILLISECONDS_IN_A_DAY * daysUntilSunday
  return getLastTimestampForGivenDate(new Date(dateOfNextSunday))
}

export const getFirstTimestampOfTheWeekEndForGivenDate = date => {
  const dayOfTheWeek = date.getDay()
  if (dayOfTheWeek === SUNDAY_INDEX_IN_A_WEEK || dayOfTheWeek === SATURDAY_INDEX_IN_A_WEEK)
    return getTimestampFromDate(date)
  const daysUntilSaturday = SATURDAY_INDEX_IN_A_WEEK - dayOfTheWeek
  const dateOfNextSaturday = date.getTime() + MILLISECONDS_IN_A_DAY * daysUntilSaturday
  return getFirstTimestampForGivenDate(new Date(dateOfNextSaturday))
}

export const getTimestampFromDate = date => {
  const dateInTimestamp =
    (date.getTime() - getTimezoneOffsetInMilliseconds(date)) / MILLISECONDS_IN_A_SECOND
  return Math.ceil(dateInTimestamp)
}

const getTimezoneOffsetInMilliseconds = date => {
  const timezoneOffset = date.getTimezoneOffset()
  return timezoneOffset * MILLISECONDS_IN_A_MINUTE
}

export const getDatesOfTheWeekEnd = date => {
  const dayOfTheWeek = date.getDay()
  if (dayOfTheWeek === SUNDAY_INDEX_IN_A_WEEK) {
    return [date]
  }
  const daysUntilSaturday = SATURDAY_INDEX_IN_A_WEEK - dayOfTheWeek
  const timestampOfNextSaturday = date.getTime() + MILLISECONDS_IN_A_DAY * daysUntilSaturday
  const dateOfNextSaturday = new Date(timestampOfNextSaturday)

  const daysUntilSunday = DAYS_IN_A_WEEK - dayOfTheWeek
  const timestampOfNextSunday = date.getTime() + MILLISECONDS_IN_A_DAY * daysUntilSunday
  const dateOfNextSunday = new Date(timestampOfNextSunday)

  return [dateOfNextSaturday, dateOfNextSunday]
}

export const getBeginningAndEndingDatesForGivenTimeRange = (date, timeRange) => {
  const beginningDatetime = getDateAtGivenTime(date, timeRange[0])
  const endingDatetime = getDateAtGivenTime(date, timeRange[1])
  return [beginningDatetime, endingDatetime]
}

export const getBeginningAndEndingTimestampsForGivenTimeRange = (date, timeRange) => {
  return getBeginningAndEndingDatesForGivenTimeRange(date, timeRange).map(date =>
    getTimestampFromDate(date)
  )
}

const getDateAtGivenTime = (date, time) => {
  if (time === 24) {
    const dateWithTime = new Date(date.setHours(23))
    dateWithTime.setMinutes(59)
    dateWithTime.setSeconds(59)
    dateWithTime.setMilliseconds(999)
    return dateWithTime
  }
  const dateWithTime = new Date(date.setHours(time))
  dateWithTime.setMinutes(0)
  dateWithTime.setSeconds(0)
  dateWithTime.setMilliseconds(0)
  return dateWithTime
}

export const getDatesOfTheWeek = date => {
  const dayOfTheWeek = date.getDay()
  if (dayOfTheWeek === SUNDAY_INDEX_IN_A_WEEK) return [date]
  let daysUntilSunday = DAYS_IN_A_WEEK - dayOfTheWeek
  const timestampsOfTheWeek = []
  while (daysUntilSunday >= 0) {
    timestampsOfTheWeek.push(date.getTime() + MILLISECONDS_IN_A_DAY * daysUntilSunday)
    daysUntilSunday--
  }
  return timestampsOfTheWeek.sort().map(timestampOfTheWeek => new Date(timestampOfTheWeek))
}

export const getTimestampsOfTheWeekEndIncludingTimeRange = (date, timeRange) => {
  const datesOfTheWeekend = getDatesOfTheWeekEnd(date)
  return getTimestampsIncludingTimeRangeForGivenDates(datesOfTheWeekend, timeRange)
}

export const getTimestampsOfTheWeekIncludingTimeRange = (date, timeRange) => {
  const datesOfTheWeek = getDatesOfTheWeek(date)
  return getTimestampsIncludingTimeRangeForGivenDates(datesOfTheWeek, timeRange)
}

const getTimestampsIncludingTimeRangeForGivenDates = (dates, timeRange) => {
  return dates.map(date =>
    getBeginningAndEndingDatesForGivenTimeRange(date, timeRange).map(dateIncludingTime =>
      getTimestampFromDate(dateIncludingTime)
    )
  )
}

export const computeTimeRangeFromHoursToSeconds = timeRange => {
  return timeRange.map(timeInHour => timeInHour * 60 * 60)
}
