import { RecurrenceDays } from './types'

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
      days.includes(jsDayToRecurrenceDayMap[currentDate.getDay()])
    ) {
      dates.push(currentDate)
    }

    // Clone date object to avoid mutating old one
    currentDate = new Date(currentDate)
    currentDate.setDate(currentDate.getDate() + 1)
  }
  return dates
}
