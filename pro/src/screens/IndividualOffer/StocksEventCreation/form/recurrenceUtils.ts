import { addMonths, endOfMonth, isToday } from 'date-fns'

import { getToday, isDateValid } from 'utils/date'

import { MonthlyOption, RecurrenceDays } from './types'

const jsDayToRecurrenceDayMap: Record<number, RecurrenceDays> = {
  // JS .getDay() returns 0 for Sunday, 1 for Monday, etc.
  0: RecurrenceDays.SUNDAY,
  1: RecurrenceDays.MONDAY,
  2: RecurrenceDays.TUESDAY,
  3: RecurrenceDays.WEDNESDAY,
  4: RecurrenceDays.THURSDAY,
  5: RecurrenceDays.FRIDAY,
  6: RecurrenceDays.SATURDAY,
}

export const isLastWeekOfMonth = (date?: Date | null): boolean => {
  if (!date || !isDateValid(date)) {
    return false
  }

  return endOfMonth(date).getDate() - date.getDate() < 7
}

export const getDatesInInterval = (
  start: Date,
  end: Date,
  days: RecurrenceDays[] = []
): Date[] => {
  const dates = []
  let currentDate = start
  while (currentDate <= end) {
    if (
      days.length === 0 ||
      (jsDayToRecurrenceDayMap[currentDate.getDay()] &&
        days.includes(jsDayToRecurrenceDayMap[currentDate.getDay()]!))
    ) {
      dates.push(currentDate)
    }

    // Clone date object to avoid mutating old one
    currentDate = new Date(currentDate)
    currentDate.setDate(currentDate.getDate() + 1)
  }
  return dates
}

export const getDatesWithMonthlyOption = (
  start: Date,
  end: Date,
  option: MonthlyOption
): Date[] => {
  const dates = []
  let currentDate = start

  switch (option) {
    case MonthlyOption.X_OF_MONTH:
      while (currentDate <= end) {
        if (start.getDate() <= endOfMonth(currentDate).getDate()) {
          currentDate.setDate(start.getDate())
          dates.push(currentDate)
        }
        // Clone date object to avoid mutating old one
        currentDate = new Date(currentDate)
        currentDate = addMonths(currentDate, 1)
      }
      return dates
    case MonthlyOption.BY_FIRST_DAY:
      while (currentDate <= end) {
        const startWeekOfMonth = Math.floor((start.getDate() - 1) / 7)
        const currentDateWeekOfMonth = Math.floor(
          (currentDate.getDate() - 1) / 7
        )
        if (
          currentDateWeekOfMonth === startWeekOfMonth &&
          currentDate.getDay() === start.getDay()
        ) {
          dates.push(currentDate)
        }
        // Clone date object to avoid mutating old one
        currentDate = new Date(currentDate)
        currentDate.setDate(currentDate.getDate() + 1)
      }
      return dates
    case MonthlyOption.BY_LAST_DAY:
      while (currentDate <= end) {
        if (
          isLastWeekOfMonth(currentDate) &&
          currentDate.getDay() === start.getDay()
        ) {
          dates.push(currentDate)
        }
        // Clone date object to avoid mutating old one
        currentDate = new Date(currentDate)
        currentDate.setDate(currentDate.getDate() + 1)
      }
      return dates
  }
}

export const isTimeInTheFuture = (
  beginningDate: Date,
  beginningTime: string
): boolean => {
  const now = getToday()
  if (beginningDate > now) {
    return true
  }
  if (!isToday(beginningDate)) {
    return false
  }
  const [hours, minutes] = beginningTime.split(':')
  if (parseInt(hours ?? '') > now.getHours()) {
    return true
  }
  if (parseInt(hours ?? '') === now.getHours()) {
    return parseInt(minutes ?? '') > now.getMinutes()
  }
  return false
}
