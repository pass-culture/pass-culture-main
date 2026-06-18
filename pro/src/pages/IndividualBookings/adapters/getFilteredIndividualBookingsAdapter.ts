import { api } from '@/apiClient/api'
import type { BookingRecapResponseModel } from '@/apiClient/v1'
import type { PreFiltersParams } from '@/commons/core/Bookings/types'
import { buildBookingsRecapQuery } from '@/commons/core/Bookings/utils'

const MAX_LOADED_PAGES = 10

export const getFilteredIndividualBookingsAdapter = async (
  apiFilters: PreFiltersParams & {
    page?: number
  },
  venueId: number,
  offerId?: number
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
      page = 1,
      eventDate,
      bookingStatusFilter,
      bookingPeriodBeginningDate,
      bookingPeriodEndingDate,
      offererAddressId,
    } = buildBookingsRecapQuery(nextPageFilters)

    const bookings = await api.getBookingsPro({
      query: {
        venueId,
        page,
        offerId,
        eventDate,
        bookingStatusFilter,
        bookingPeriodBeginningDate,
        bookingPeriodEndingDate,
        offererAddressId,
      },
    })
    pages = bookings.pages

    allBookings = [...allBookings, ...bookings.bookingsRecap]
  } while (currentPage < Math.min(pages, MAX_LOADED_PAGES))

  return {
    bookings: allBookings,
    pages,
    currentPage,
  }
}
