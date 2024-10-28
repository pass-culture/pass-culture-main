import { format } from 'date-fns'

import { getLocalDepartementDateTimeFromUtc } from 'commons/utils/timezone'

export const formatDateTime = (
  date: string,
  dateFormat: string,
  venueDepartmentCode?: string | null
) => {
  return format(
    getLocalDepartementDateTimeFromUtc(
      new Date(date),
      venueDepartmentCode || undefined
    ),
    dateFormat
  )
}
