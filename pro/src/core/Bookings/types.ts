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

export type APIFilters = {
  venueId: string
  eventDate: string
  bookingPeriodBeginningDate: string
  bookingPeriodEndingDate: string
  bookingStatusFilter: BookingStatusFilter
  offerType: string
  offerId?: string
  page: number
}

export type GetUserHasBookingsAdapter = Adapter<void, boolean, boolean>

export type VenuesPayload = { venues: { value: string; label: string }[] }
export type GetVenuesAdapter = Adapter<void, VenuesPayload, VenuesPayload>
