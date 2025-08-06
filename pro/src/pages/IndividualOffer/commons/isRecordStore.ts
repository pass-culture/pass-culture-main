import { VenueTypeCode } from '@/apiClient//v1'

export const isRecordStore = (
  venues: { venueTypeCode: VenueTypeCode }[]
): boolean => {
  return venues.some(
    (venue) => venue.venueTypeCode === ('RECORD_STORE' as VenueTypeCode)
  )
}
