import { api } from '@/apiClient/api'
import type { BookingRecapResponseModel } from '@/apiClient/v1'
import type { PreFiltersParams } from '@/commons/core/Bookings/types'
import { buildBookingsRecapQuery } from '@/commons/core/Bookings/utils'
import type { RootState } from '@/commons/store/store'

const MAX_LOADED_PAGES = 5

export const getFilteredAdminIndividualBookingsAdapter = async (
  apiFilters: PreFiltersParams & { page?: number },
  getState: () => RootState
) => {
  const state = getState()
  const adminOfferer = state.offerer.adminCurrentOfferer

  // Override offererId with adminCurrentOfferer if available
  const filtersWithAdminOfferer = {
    ...apiFilters,
    offererId: adminOfferer?.id
      ? String(adminOfferer.id)
      : apiFilters.offererId,
  }

  let allBookings: BookingRecapResponseModel[] = []
  let currentPage = 0
  let pages: number

  do {
    currentPage += 1
    const nextPageFilters = {
      ...filtersWithAdminOfferer,
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
