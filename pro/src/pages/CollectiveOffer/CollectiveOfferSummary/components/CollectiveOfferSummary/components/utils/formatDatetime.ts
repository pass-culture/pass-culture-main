import { getLocalDepartementDateTimeFromUtc } from 'commons/utils/timezone'
import { format } from 'date-fns'
import { fr } from 'date-fns/locale'

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
    dateFormat,
    { locale: fr }
  )
}
