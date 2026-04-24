import type { WeekdayOpeningHoursTimespansV2 } from '@/apiClient/v1'

export function areOpeningHoursEmpty(
  openingHours?: WeekdayOpeningHoursTimespansV2 | null
) {
  if (!openingHours) {
    return true
  }

  return Object.values(openingHours).every((day) => !day || day.length === 0)
}
