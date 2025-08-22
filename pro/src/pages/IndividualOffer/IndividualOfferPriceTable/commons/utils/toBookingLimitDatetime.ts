import { endOfDay, parse } from 'date-fns'

import {
  FORMAT_ISO_DATE_ONLY,
  isDateValid,
  toISOStringWithoutMilliseconds,
} from '@/commons/utils/date'
import { getUtcDateTimeFromLocalDepartement } from '@/commons/utils/timezone'

export const toBookingLimitDatetime = (
  dateLike: string | Date | null | undefined,
  departementCode?: string | null
): string | null => {
  if (!isDateValid(dateLike as Date | string | null | undefined)) {
    return null
  }
  const dateObject =
    typeof dateLike === 'string'
      ? parse(dateLike, FORMAT_ISO_DATE_ONLY, new Date())
      : (dateLike as Date)
  const utc = getUtcDateTimeFromLocalDepartement(
    endOfDay(dateObject),
    departementCode
  )
  return toISOStringWithoutMilliseconds(utc)
}
