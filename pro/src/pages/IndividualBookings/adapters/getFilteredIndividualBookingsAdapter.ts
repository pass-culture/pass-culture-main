import { api } from '@/apiClient/api'
import type { BookingStatus } from '@/apiClient/v1'
import type { PreFiltersParams } from '@/commons/core/Bookings/types'
import { buildBookingsRecapQuery } from '@/commons/core/Bookings/utils'

export type OmniSearchParams = {
  offerName?: string
  beneficiaryNameOrEmail?: string
  offerEan?: string
  bookingToken?: string
  bookingStatus?: BookingStatus[]
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
    apiFilters.bookingStatus
  )

  return {
    bookings: bookings.bookingsRecap,
    pages: bookings.pages,
    total: bookings.total,
    currentPage: bookings.page,
  }
}
