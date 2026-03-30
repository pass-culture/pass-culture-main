import { api } from '@/apiClient/api'
import type { BookingRecapStatus, BookingSortableColumn, SortOrder } from '@/apiClient/v1'
import type { PreFiltersParams } from '@/commons/core/Bookings/types'
import { buildBookingsRecapQuery } from '@/commons/core/Bookings/utils'

export type OmniSearchParams = {
  offerName?: string
  beneficiaryNameOrEmail?: string
  offerEan?: string
  bookingToken?: string
  bookingStatus?: BookingRecapStatus[]
  sortBy?: BookingSortableColumn
  sortOrder?: SortOrder
}

export const getFilteredIndividualBookingsAdapter = async (
  apiFilters: PreFiltersParams & { page: number } & OmniSearchParams
) => {
  const {
    venueId,
    offererId,
    offererAddressId,
    offerId,
    eventDate,
    bookingPeriodBeginningDate,
    bookingPeriodEndingDate,
    eventType,
    page,
  } = buildBookingsRecapQuery(apiFilters)

  const bookings = await api.getBookingsPro(
    page,
    // @ts-expect-error api expect number
    offererId,
    venueId,
    offerId,
    eventDate,
    eventType,
    bookingPeriodBeginningDate,
    bookingPeriodEndingDate,
    offererAddressId,
    undefined,
    apiFilters.offerName,
    apiFilters.beneficiaryNameOrEmail,
    apiFilters.offerEan,
    apiFilters.bookingToken,
    apiFilters.bookingStatus,
    apiFilters.sortBy,
    apiFilters.sortOrder,
  )

  return {
    bookings: bookings.bookingsRecap,
    pages: bookings.pages,
    total: bookings.total,
    currentPage: bookings.page,
  }
}
