import { BookingRecapResponseModel, BookingStatusFilter } from 'api/v1/gen'

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

type EducationalRedactorResponseModel = {
  email: string
  firstname: string
  lastname: string
  phonenumber?: string | null
}

type BookingStatusHistoryResponseModel = {
  date: string
  status: string
}

type CollectiveStockResponseModel = {
  eventBeginningDatetime: string
  offerIdentifier: string
  offerIsEducational?: boolean
  offerIsbn?: string | null
  offerName: string
}

export type CollectiveBookingResponseModel = {
  beneficiary: EducationalRedactorResponseModel
  bookingAmount: number
  bookingDate: string
  bookingIsDuo?: boolean
  bookingStatus: string
  bookingStatusHistory: BookingStatusHistoryResponseModel[]
  bookingToken?: string | null
  stock: CollectiveStockResponseModel
}

export type CollectiveBookingsResponseModel = {
  bookingsRecap: CollectiveBookingResponseModel[]
  page: number
  pages: number
  total: number
}
