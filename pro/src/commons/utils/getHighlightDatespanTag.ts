import { formatDate } from '@/commons/utils/date'

export function getHighlightDatespanTag(
  highlightDatespan: Array<string>
): string {
  const formattedStartDate = formatDate(highlightDatespan[0])
  const formattedEndDate = formatDate(highlightDatespan[1])

  if (formattedStartDate === formattedEndDate) {
    return formattedStartDate
  }

  return `${formattedStartDate} au ${formattedEndDate}`
}
