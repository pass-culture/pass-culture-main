import {
  BookingStatusFilter,
  CollectiveBookingStatusFilter,
} from 'apiClient/v1'

export type PreFiltersParams = {
  offerVenueId: string
  offererAddressId: string
  offerEventDate: string
  bookingBeginningDate: string
  bookingEndingDate: string
  bookingStatusFilter: BookingStatusFilter | CollectiveBookingStatusFilter
  offerId?: string
}

export type APIFilters = {
  venueId: string
  offererAddressId: string
  eventDate: string
  bookingPeriodBeginningDate: string
  bookingPeriodEndingDate: string
  bookingStatusFilter: BookingStatusFilter | CollectiveBookingStatusFilter
  offerId?: string
  page: number
}
