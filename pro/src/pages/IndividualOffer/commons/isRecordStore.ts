import type { DisplayableActivity } from '@/apiClient/v1/new'

export const isRecordStore = (
  venues: { activity?: DisplayableActivity | null }[]
): boolean => {
  return venues.some(
    (venue) => venue.activity === ('RECORD_STORE' as DisplayableActivity)
  )
}
