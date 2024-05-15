import { api } from 'apiClient/api'
import { CollectiveBookingResponseModel } from 'apiClient/v1'
import { PreFiltersParams } from 'core/Bookings/types'
import { buildBookingsRecapQuery } from 'core/Bookings/utils'

const MAX_LOADED_PAGES = 5

export const getFilteredCollectiveBookingsAdapter = async (
  apiFilters: PreFiltersParams & { page?: number }
) => {
  let allBookings: CollectiveBookingResponseModel[] = []
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
      eventDate,
      bookingPeriodBeginningDate,
      bookingPeriodEndingDate,
      bookingStatusFilter,
      page,
    } = buildBookingsRecapQuery(nextPageFilters)

    const bookings = await api.getCollectiveBookingsPro(
      page,
      // @ts-expect-error type string is not assignable to type number
      venueId,
      eventDate,
      bookingStatusFilter,
      bookingPeriodBeginningDate,
      bookingPeriodEndingDate
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
