import { format } from 'date-fns-tz'

import { FORMAT_DD_MM_YYYY, toDateStrippedOfTimezone } from 'utils/date'

type Stock = {
  remainingQuantity?: string | number
  bookingLimitDatetime?: Date | null
}

export const getRemainingTime = (stock: Stock[]) => {
  const { bookingLimitDatetime } = stock[0]
  if (!bookingLimitDatetime) {
    return -1
  }

  const date = new Date()
  const time_diff = new Date(bookingLimitDatetime).getTime() - date.getTime()
  const days_Diff = time_diff / (1000 * 3600 * 24)

  return Math.floor(days_Diff)
}

export const shouldDisplayWarning = (stock: Stock[]) => {
  const differenceDay = getRemainingTime(stock)

  if (differenceDay >= 7 || differenceDay < 0) {
    return false
  }
  return true
}

export const getDate = (stock: Stock[]) => {
  const { bookingLimitDatetime } = stock[0]

  if (!bookingLimitDatetime) {
    return undefined
  }

  return format(
    toDateStrippedOfTimezone(bookingLimitDatetime.toString()),
    FORMAT_DD_MM_YYYY
  )
}
