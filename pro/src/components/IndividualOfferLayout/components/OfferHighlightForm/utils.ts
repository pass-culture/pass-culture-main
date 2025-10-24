import { formatDate } from '@/commons/utils/date'

export function getDateTag(startDate: string, endDate: string): string {
  const formattedStartDate = formatDate(startDate)
  const formattedEndDate = formatDate(endDate)

  if (formattedStartDate === formattedEndDate) {
    return formattedStartDate
  }

  return `${formattedStartDate} au ${formattedEndDate}`
}
