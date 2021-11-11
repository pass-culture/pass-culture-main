const DAYS_IN_A_WEEK = 7
const SATURDAY_INDEX_IN_A_WEEK = 6
const SUNDAY_INDEX_IN_A_WEEK = 0

const MILLISECONDS_IN_A_DAY = 24 * 60 * 60 * 1000
const FIVE_MINUTES = 5 * 60 * 1000

/**
 * Transform functions: from one date, get a specific time of this date:
 * - getStartOfDay
 * - getDateAtGivenHour
 * - getEndOfDay
 */
const getStartOfDay = date =>
  new Date(date.getFullYear(), date.getMonth(), date.getDate(), 0, 0, 0, 0)

const getDateAtGivenHour = (date, hours) =>
  new Date(date.getFullYear(), date.getMonth(), date.getDate(), hours, 0, 0, 0)

const getEndOfDay = date =>
  new Date(date.getFullYear(), date.getMonth(), date.getDate(), 23, 59, 59, 0)

/**
 * Fetch functions: from one date, get another date in the week or weekend, or a list of dates:
 * - getEndOfWeek
 * - getStartOfWeekEnd
 * - getWeekDatesFromDate
 * - getWeekEndDatesFromDate
 */
const getEndOfWeek = date => {
  const dayOfTheWeek = date.getDay()
  if (dayOfTheWeek === SUNDAY_INDEX_IN_A_WEEK) return getEndOfDay(date)

  const daysUntilSunday = DAYS_IN_A_WEEK - dayOfTheWeek
  const dateOfNextSunday = date.getTime() + MILLISECONDS_IN_A_DAY * daysUntilSunday
  return getEndOfDay(new Date(dateOfNextSunday))
}

const getStartOfWeekEnd = date => {
  const dayOfTheWeek = date.getDay()
  if (dayOfTheWeek === SUNDAY_INDEX_IN_A_WEEK || dayOfTheWeek === SATURDAY_INDEX_IN_A_WEEK)
    return getStartOfDay(date)

  const daysUntilSaturday = SATURDAY_INDEX_IN_A_WEEK - dayOfTheWeek
  const dateOfNextSaturday = date.getTime() + MILLISECONDS_IN_A_DAY * daysUntilSaturday
  return getStartOfDay(new Date(dateOfNextSaturday))
}

const getWeekDatesFromDate = date => {
  const dayOfTheWeek = date.getDay()
  if (dayOfTheWeek === SUNDAY_INDEX_IN_A_WEEK) return [date]

  const daysUntilSunday = DAYS_IN_A_WEEK - dayOfTheWeek
  return Array.from({ length: daysUntilSunday + 1 }).map(
    (_, day) => new Date(date.getTime() + MILLISECONDS_IN_A_DAY * day)
  )
}

const getWeekEndDatesFromDate = date => {
  const dayOfTheWeek = date.getDay()
  if (dayOfTheWeek === SUNDAY_INDEX_IN_A_WEEK) return [date]

  const daysUntilSaturday = SATURDAY_INDEX_IN_A_WEEK - dayOfTheWeek
  const timestampOfNextSaturday = date.getTime() + MILLISECONDS_IN_A_DAY * daysUntilSaturday
  const dateOfNextSaturday = new Date(timestampOfNextSaturday)

  const daysUntilSunday = DAYS_IN_A_WEEK - dayOfTheWeek
  const timestampOfNextSunday = date.getTime() + MILLISECONDS_IN_A_DAY * daysUntilSunday
  const dateOfNextSunday = new Date(timestampOfNextSunday)

  return [dateOfNextSaturday, dateOfNextSunday]
}

/**
 * Mapping functions: from one or multiple dates, get time ranges
 */
const getTimestampsFromTimeRangeAndDate = (date, timeRange) =>
  timeRange.map(hour => getDateAtGivenHour(date, hour))

const getTimestampsFromTimeRangeAndDates = (dates, timeRange) =>
  dates.map(date => getTimestampsFromTimeRangeAndDate(date, timeRange))

const getWeekTimestampsFromTimeRangeAndDate = (date, timeRange) =>
  getTimestampsFromTimeRangeAndDates(TIME.WEEK.getWeekDatesFromDate(date), timeRange)

const getWeekEndTimestampsFromTimeRangeAndDate = (date, timeRange) =>
  getTimestampsFromTimeRangeAndDates(TIME.WEEK_END.getWeekEndDatesFromDate(date), timeRange)

/**
 * Utils functions
 */
const roundToNearestFiveMinutes = date =>
  new Date(Math.round(date.getTime() / FIVE_MINUTES) * FIVE_MINUTES)

const computeTimeRangeFromHoursToSeconds = timeRange => {
  const offsetInMinutes = new Date().getTimezoneOffset()
  return timeRange.map(timeInHour => (timeInHour * 60 + offsetInMinutes) * 60)
}

export const TIME = {
  getStartOfDay,
  getDateAtGivenHour,
  getEndOfDay,
  getStartOfWeekEnd,
  getEndOfWeek,
  getAllFromTimeRangeAndDate: getTimestampsFromTimeRangeAndDate,
  WEEK_END: {
    getWeekEndDatesFromDate,
    getAllFromTimeRangeAndDate: getWeekEndTimestampsFromTimeRangeAndDate,
  },
  WEEK: {
    getWeekDatesFromDate,
    getAllFromTimeRangeAndDate: getWeekTimestampsFromTimeRangeAndDate,
  },
  computeTimeRangeFromHoursToSeconds,
  roundToNearestFiveMinutes,
}
