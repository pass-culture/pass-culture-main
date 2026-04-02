import type { BookingEventType } from '@/apiClient/v1'

export type PreFiltersParams = {
  offererId: string
  offerVenueId: string
  offererAddressId: string
  offerEventDate: string
  bookingBeginningDate: string
  bookingEndingDate: string
  eventType: BookingEventType
  offerId?: string
}

export type APIFilters = {
  offererId: string
  venueId: string
  offererAddressId: string
  eventDate: string
  bookingPeriodBeginningDate: string
  bookingPeriodEndingDate: string
  eventType: BookingEventType
  offerId?: string
  page: number
}
