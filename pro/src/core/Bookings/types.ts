import { BookingStatusFilter } from 'apiClient/v1'

export type PreFiltersParams = {
  offerVenueId: string
  offerEventDate: string
  bookingBeginningDate: string
  bookingEndingDate: string
  bookingStatusFilter: BookingStatusFilter
  offerType: string
  offerId?: string
}
