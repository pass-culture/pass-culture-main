import { api } from 'apiClient/api'
import { CollectiveBookingResponseModel } from 'apiClient/v1'
import { DEFAULT_PRE_FILTERS } from 'core/Bookings/constants'
import { PreFiltersParams } from 'core/Bookings/types'
import { isDateValid } from 'utils/date'

const MAX_LOADED_PAGES = 5

export const getFilteredCollectiveBookingsAdapter = async (
  apiFilters: PreFiltersParams & { page?: number }
) => {
  let allBookings: CollectiveBookingResponseModel[] = []
  let currentPage = 0
  let pages: number

  do {
    currentPage += 1

    const bookings = await api.getCollectiveBookingsPro(
      currentPage,
      // @ts-expect-error type string is not assignable to type number
      apiFilters.offerVenueId !== DEFAULT_PRE_FILTERS.offerVenueId
        ? apiFilters.offerVenueId
        : undefined,
      apiFilters.offerEventDate !== DEFAULT_PRE_FILTERS.offerEventDate
        ? apiFilters.offerEventDate
        : undefined,
      apiFilters.bookingStatusFilter,
      isDateValid(apiFilters.bookingBeginningDate)
        ? apiFilters.bookingBeginningDate
        : undefined,
      isDateValid(apiFilters.bookingEndingDate)
        ? apiFilters.bookingEndingDate
        : undefined
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
