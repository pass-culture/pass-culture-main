import { api } from 'apiClient/api'
import { BookingRecapResponseModel } from 'apiClient/v1'
import { DEFAULT_PRE_FILTERS } from 'core/Bookings/constants'
import { PreFiltersParams } from 'core/Bookings/types'
import { isDateValid } from 'utils/date'

const MAX_LOADED_PAGES = 5

export const getFilteredIndividualBookingsAdapter = async (
  apiFilters: PreFiltersParams & { page?: number }
) => {
  let allBookings: BookingRecapResponseModel[] = []
  let currentPage = 0
  let pages: number

  do {
    currentPage += 1

    const bookings = await api.getBookingsPro(
      currentPage,
      // @ts-expect-error api expect number
      apiFilters.offerVenueId !== DEFAULT_PRE_FILTERS.offerVenueId
        ? apiFilters.offerVenueId
        : undefined,
      apiFilters.offerId !== DEFAULT_PRE_FILTERS.offerId
        ? apiFilters.offerId
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
        : undefined,
      apiFilters.offerType !== DEFAULT_PRE_FILTERS.offerType
        ? apiFilters.offerType
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
