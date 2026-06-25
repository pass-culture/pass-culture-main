import type { ExposureEventResponseModel } from '@/apiClient/v1'

export const isOngoing = (event: ExposureEventResponseModel): boolean => {
  return !event.endDate || new Date(event.endDate) > new Date()
}
