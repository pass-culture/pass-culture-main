import { api } from '@/apiClient//api'
import { BookingRecapResponseModel } from '@/apiClient//v1'
import { PreFiltersParams } from '@/commons/core/Bookings/types'
import { buildBookingsRecapQuery } from '@/commons/core/Bookings/utils'

const MAX_LOADED_PAGES = 5

export const getFilteredIndividualBookingsAdapter = async (
  apiFilters: PreFiltersParams & { page?: number }
) => {
  let allBookings: BookingRecapResponseModel[] = []
  let currentPage = 0
  let pages: number

  do {
    currentPage += 1
    const nextPageFilters = {
      ...apiFilters,
      page: currentPage,
    }
    const {
      venueId,
      offererId,
      offererAddressId,
      offerId,
      eventDate,
      bookingPeriodBeginningDate,
      bookingPeriodEndingDate,
      bookingStatusFilter,
      page,
    } = buildBookingsRecapQuery(nextPageFilters)

    const bookings = await api.getBookingsPro(
      page,
      // @ts-expect-error api expect number
      offererId,
      venueId,
      offerId,
      eventDate,
      bookingStatusFilter,
      bookingPeriodBeginningDate,
      bookingPeriodEndingDate,
      offererAddressId
    )
    pages = bookings.pages

    allBookings = [...allBookings, ...bookings.bookingsRecap]
  } while (currentPage < Math.min(pages, MAX_LOADED_PAGES))

  return {
    bookings: allBookings,
    pages,
    currentPage,
  }
}
