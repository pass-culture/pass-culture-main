import type { VenueTypeCodeKey } from '@/apiClient/v1'

export const isRecordStore = (
  venues: { venueTypeCode: VenueTypeCodeKey }[]
): boolean => {
  return venues.some(
    (venue) => venue.venueTypeCode === ('RECORD_STORE' as VenueTypeCodeKey)
  )
}
