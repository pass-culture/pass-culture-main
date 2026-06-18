import type { WeekdayOpeningHoursTimespans } from '@/apiClient/v1'

export function areOpeningHoursEmpty(
  openingHours?: WeekdayOpeningHoursTimespans | null
) {
  if (!openingHours) {
    return true
  }

  return Object.values(openingHours).every((day) => !day || day.length === 0)
}
