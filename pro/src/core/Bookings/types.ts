import { BookingStatusFilter } from 'api/v1/gen'

export type TPreFilters = {
  offerVenueId: string
  offerEventDate: Date | string
  bookingBeginningDate: Date
  bookingEndingDate: Date
  bookingStatusFilter: BookingStatusFilter
  offerType: string
}

export type TAPIFilters = {
  venueId: string
  eventDate: string
  bookingPeriodBeginningDate: string
  bookingPeriodEndingDate: string
  bookingStatusFilter: BookingStatusFilter
  offerType: string
  page: number
}
