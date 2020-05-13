import { MILLISECONDS_IN_A_DAY } from './time'

export const DAYS_IN_A_WEEK = 7
export const SATURDAY_INDEX_IN_A_WEEK = 6
export const SUNDAY_INDEX_IN_A_WEEK = 0

export const getDatesFromTimeRangeAndDate = (date, timeRange) => {
  const beginningDatetime = getDateAtGivenTime(date, timeRange[0])
  const endingDatetime = getDateAtGivenTime(date, timeRange[1])
  return [beginningDatetime, endingDatetime]
}

const getDateAtGivenTime = (date, time) => {
  const offsetInHours = date.getTimezoneOffset() / 60
  const sign = Math.sign(offsetInHours)

  let timeAdaptedToTimeZone
  if (sign === 1) {
    timeAdaptedToTimeZone = time - offsetInHours
  } else {
    timeAdaptedToTimeZone = time + offsetInHours
  }

  const dateWithTime = new Date(date.getTime())
  dateWithTime.setHours(timeAdaptedToTimeZone)
  dateWithTime.setMinutes(0)
  dateWithTime.setSeconds(0)
  dateWithTime.setMilliseconds(0)
  return dateWithTime
}

const getWeekDatesFromDate = date => {
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

const getWeekEndDatesFromDate = date => {
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

export const DATE = {
  getAllFromTimeRangeAndDate: getDatesFromTimeRangeAndDate,
  WEEK: {
    getAllFromDate: getWeekDatesFromDate,
  },
  WEEK_END: {
    getAllFromDate: getWeekEndDatesFromDate,
  },
}
