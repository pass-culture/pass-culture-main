import type { BookingStatusFilter } from '@/apiClient/v1'

export type PreFiltersParams = {
  offererId: string
  offerVenueId: string
  offererAddressId: string
  offerEventDate: string
  bookingBeginningDate: string
  bookingEndingDate: string
  bookingStatusFilter: BookingStatusFilter
  offerId?: string
}

export type APIFilters = {
  offererId: string
  venueId: string
  offererAddressId: string
  eventDate: string
  bookingPeriodBeginningDate: string
  bookingPeriodEndingDate: string
  bookingStatusFilter: BookingStatusFilter
  offerId?: string
  page: number
}
