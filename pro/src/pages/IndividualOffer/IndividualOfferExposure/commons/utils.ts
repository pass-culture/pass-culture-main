import type { ExposureEventResponseModel } from '@/apiClient/v1'

// An enhancement is ongoing while it has no end date yet, or its end date is
// still in the future.
export const isOngoing = (event: ExposureEventResponseModel): boolean => {
  return !event.endDate || new Date(event.endDate) > new Date()
}
