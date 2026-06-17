import { format } from 'date-fns'

import { FORMAT_HH_mm, FORMAT_ISO_DATE_ONLY } from '@/commons/utils/date'
import { getLocalDepartementDateTimeFromUtc } from '@/commons/utils/timezone'

import type {
  CollectiveStockDatetimes,
  CollectiveStockFormDates,
} from './types'

export const extractFormDates = (
  {
    startDatetime,
    endDatetime,
    bookingLimitDatetime,
  }: Partial<CollectiveStockDatetimes>,
  departementCode?: string
): CollectiveStockFormDates => {
  const dates: CollectiveStockFormDates = {
    startDate: '',
    endDate: '',
    eventTime: '',
    bookingLimitDate: '',
  }

  if (startDatetime) {
    dates.startDate = format(
      getLocalDepartementDateTimeFromUtc(startDatetime, departementCode),
      FORMAT_ISO_DATE_ONLY
    )
    if (startDatetime.length > FORMAT_ISO_DATE_ONLY.length)
      dates.eventTime = format(
        getLocalDepartementDateTimeFromUtc(startDatetime, departementCode),
        FORMAT_HH_mm
      )
  }

  if (endDatetime) {
    dates.endDate = format(
      getLocalDepartementDateTimeFromUtc(endDatetime, departementCode),
      FORMAT_ISO_DATE_ONLY
    )
  }

  if (bookingLimitDatetime) {
    dates.bookingLimitDate = format(
      getLocalDepartementDateTimeFromUtc(bookingLimitDatetime, departementCode),
      FORMAT_ISO_DATE_ONLY
    )
  }

  return dates
}
