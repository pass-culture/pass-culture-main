import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'

import { BookingStatusFilter } from 'apiClient/v1'

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

export type GetFilteredBookingsRecapAdapterPayload = {
  bookings: BookingRecapResponseModel[]
  pages: number
  currentPage: number
}

export type GetFilteredCollectiveBookingsRecapAdapterPayload = {
  bookings: CollectiveBookingResponseModel[]
  pages: number
  currentPage: number
}

export type GetFilteredBookingsRecapAdapter = Adapter<
  TPreFilters & { page?: number },
  GetFilteredBookingsRecapAdapterPayload,
  GetFilteredBookingsRecapAdapterPayload
>

export type GetFilteredCollectiveBookingsRecapAdapter = Adapter<
  TPreFilters & { page?: number },
  GetFilteredCollectiveBookingsRecapAdapterPayload,
  GetFilteredCollectiveBookingsRecapAdapterPayload
>

export type GetBookingsCSVFileAdapter = Adapter<
  TPreFilters & { page?: number },
  null,
  null
>

export type GetBookingsXLSFileAdapter = Adapter<
  TPreFilters & { page?: number },
  null,
  null
>

export type GetUserHasBookingsAdapter = Adapter<void, boolean, boolean>

export type VenuesPayload = { venues: { id: string; displayName: string }[] }
export type GetVenuesAdapter = Adapter<void, VenuesPayload, VenuesPayload>
